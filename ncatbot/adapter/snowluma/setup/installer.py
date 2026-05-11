"""SnowLuma 下载与解压。

从 GitHub Releases 拉取 ``SnowLuma-vX.Y.Z-win-x64[-lite].zip``，解压到
``platform_ops.snowluma_dir``。版本号优先走 ``releases/latest`` 重定向（不
受 GitHub API 限额影响），失败时回退到 ``/tags`` API。所有 GitHub 流量都
经 ``gen_url_with_proxy`` 走 NcatBot 配置的 GitHub 代理。
"""

from __future__ import annotations

import os
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Optional

import httpx
from tqdm import tqdm

from ncatbot.utils import gen_url_with_proxy, get_json, get_log

from ..constants import (
    SNOWLUMA_LATEST_RELEASE_URL,
    SNOWLUMA_TAGS_API_URL,
    windows_asset_url,
)
from .platform import PlatformOps, WindowsOps

LOG = get_log("SnowLumaInstaller")


# ---------------------------------------------------------------
# 文件操作工具（与 napcat installer 等价；独立一份避免跨适配器耦合）
# ---------------------------------------------------------------


def _download_file(url: str, dest: str) -> None:
    """带进度条下载文件到 ``dest``。失败时抛 ``httpx`` 异常。"""
    with httpx.stream("GET", url, follow_redirects=True, timeout=120) as r:
        r.raise_for_status()
        total_size = int(r.headers.get("content-length", 0))

        progress_bar = tqdm(
            total=total_size,
            unit="iB",
            unit_scale=True,
            desc=f"Downloading {os.path.basename(dest)}",
            bar_format=(
                "{l_bar}{bar}| {n_fmt}/{total_fmt} "
                "[{elapsed}<{remaining}, {rate_fmt}]"
            ),
            colour="green",
            dynamic_ncols=True,
        )

        with open(dest, "wb") as f:
            for data in r.iter_bytes(chunk_size=1024):
                progress_bar.update(len(data))
                f.write(data)

        progress_bar.close()


def _unzip(zip_path: str, extract_to: str, *, remove: bool = False) -> None:
    """解压 ZIP，可选删除原文件。"""
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_to)
        LOG.info("解压完成: %s -> %s", zip_path, extract_to)
    if remove:
        try:
            os.remove(zip_path)
        except OSError as e:
            LOG.warning("删除临时 zip 失败 (非致命): %s", e)


# ---------------------------------------------------------------
# 安装器
# ---------------------------------------------------------------


class SnowLumaInstaller:
    """SnowLuma 安装 / 更新管理器。"""

    def __init__(
        self,
        platform_ops: PlatformOps,
        *,
        snowluma_config=None,
    ) -> None:
        self._platform = platform_ops
        self._config = snowluma_config

    # ----------------------------------------------------------
    # 版本号获取
    # ----------------------------------------------------------

    @staticmethod
    def _get_version_from_redirect() -> Optional[str]:
        """通过 ``releases/latest`` 重定向获取最新版本号（不依赖 API 限额）。"""
        try:
            resp = httpx.head(
                SNOWLUMA_LATEST_RELEASE_URL,
                follow_redirects=True,
                timeout=10,
            )
            # 最终 URL 形如 https://github.com/SnowLuma/SnowLuma/releases/tag/v1.7.5
            tail = str(resp.url).rsplit("/", 1)[-1]
            version = tail.lstrip("v").strip()
            if version:
                LOG.debug("通过重定向获取 SnowLuma 最新版本: %s", version)
                return version
        except Exception as e:
            LOG.error("通过 release 重定向获取版本失败: %s", e)
        return None

    @staticmethod
    def get_latest_version() -> Optional[str]:
        """先走 ``/tags`` API，失败回退到 ``releases/latest`` 重定向。"""
        LOG.info("正在获取 SnowLuma 版本信息: %s", SNOWLUMA_TAGS_API_URL)
        try:
            data = get_json(SNOWLUMA_TAGS_API_URL, timeout=10)
            if data and isinstance(data, list) and len(data) > 0:
                version = data[0].get("name", "").lstrip("v").strip()
                if version:
                    LOG.debug("获取最新版本成功 (API): %s", version)
                    return version
            LOG.warning("/tags API 未返回有效版本，回退到重定向")
        except Exception as e:
            LOG.warning("/tags API 调用失败 (%s)，回退到重定向", e)

        return SnowLumaInstaller._get_version_from_redirect()

    # ----------------------------------------------------------
    # 安装入口
    # ----------------------------------------------------------

    def install(self, *, skip_confirm: bool = False) -> bool:
        """显式安装入口（CLI ``ncatbot snowluma install`` 调用）。"""
        return self._install("install", skip_confirm=skip_confirm)

    def ensure_installed(self, *, skip_confirm: bool = False) -> bool:
        """确保 SnowLuma 已安装；启用 ``enable_update_check`` 时检查更新。"""
        if not self._platform.is_snowluma_installed():
            return self._install("install", skip_confirm=skip_confirm)

        enable_check = bool(self._config and self._config.enable_update_check)
        if not enable_check:
            return True

        current = self._platform.get_installed_version()
        latest = self.get_latest_version()
        if current and latest and current != latest:
            LOG.info("发现 SnowLuma 新版本: %s (当前: %s)", latest, current)
            return self._install("update", skip_confirm=skip_confirm)

        LOG.info("当前 SnowLuma 已是最新版本")
        return True

    # ----------------------------------------------------------
    # 内部实现
    # ----------------------------------------------------------

    def _install(self, install_type: str, *, skip_confirm: bool) -> bool:
        if isinstance(self._platform, WindowsOps):
            return self._install_windows(install_type, skip_confirm=skip_confirm)
        # Linux/macOS 暂不支持
        from .platform import UnsupportedPlatformError

        raise UnsupportedPlatformError(
            "SnowLuma 自动安装目前仅支持 Windows x64 (release 也提供 linux 包，"
            "但本阶段未实现; 请手动下载并使用 skip_setup: true)。"
        )

    def _install_windows(self, install_type: str, *, skip_confirm: bool) -> bool:
        from ncatbot.utils import confirm  # 延迟导入避免循环

        if not skip_confirm:
            prompt = (
                "未找到 SnowLuma，是否自动下载并安装？\n输入 Y 继续 / N 退出: "
                if install_type == "install"
                else "发现 SnowLuma 新版本，输入 Y 更新 / N 跳过: "
            )
            if not confirm(prompt, default=False):
                return False

        version = self.get_latest_version()
        if not version:
            LOG.error("无法获取 SnowLuma 最新版本号，请检查网络或 GitHub 代理设置")
            return False

        use_lite = bool(self._config and self._config.use_lite_package)
        original_url = windows_asset_url(version, lite=use_lite)
        download_url = gen_url_with_proxy(original_url)
        LOG.info("下载链接: %s", download_url)

        target_dir: Path = self._platform.snowluma_dir

        try:
            # 确保父目录存在
            target_dir.parent.mkdir(parents=True, exist_ok=True)

            # 更新模式：先备份 config/，再清空目录
            backup_dir: Optional[Path] = None
            if install_type == "update" and target_dir.exists():
                cfg = self._platform.config_dir
                if cfg.exists():
                    backup_dir = target_dir.parent / ".snowluma_config_backup"
                    if backup_dir.exists():
                        shutil.rmtree(backup_dir)
                    shutil.copytree(cfg, backup_dir)
                    LOG.info("已备份配置目录: %s -> %s", cfg, backup_dir)
                shutil.rmtree(target_dir)

            # 关键修复：在隔离的临时目录中下载 + 解压，再整体移动到 target_dir。
            # 避免 zip 内部是"散落文件"形式时污染上级工作目录（实测 SnowLuma
            # win-x64 zip 就是这种形态：根级直接是 node.exe / index.mjs / ...）。
            with tempfile.TemporaryDirectory(
                prefix="snowluma_install_", dir=str(target_dir.parent)
            ) as tmp:
                tmp_path = Path(tmp)
                zip_path = str(tmp_path / "snowluma.zip")

                LOG.info("正在下载 SnowLuma v%s...", version)
                _download_file(download_url, zip_path)

                extract_root = tmp_path / "extracted"
                extract_root.mkdir()
                _unzip(zip_path, str(extract_root), remove=True)

                # 自适应：zip 内可能是"单个顶层目录形式"（如
                # SnowLuma-v1.7.5-win-x64/）也可能是"散落文件形式"
                # （根直接是 node.exe / index.mjs 等）。
                payload_dir = self._resolve_payload_dir(extract_root)
                if payload_dir is None:
                    LOG.error("解压结果异常：临时目录 %s 没有有效内容", extract_root)
                    return False

                # 移动到目标目录（覆盖式）
                if target_dir.exists():
                    shutil.rmtree(target_dir)
                shutil.move(str(payload_dir), str(target_dir))

            # 还原配置
            if backup_dir is not None:
                cfg = self._platform.config_dir
                if cfg.exists():
                    shutil.rmtree(cfg)
                shutil.copytree(backup_dir, cfg)
                shutil.rmtree(backup_dir)
                LOG.info("已还原配置目录: %s", cfg)

            # 后置校验：必须存在 launcher.bat + index.mjs，否则视为安装失败
            if not self._platform.is_snowluma_installed():
                LOG.error(
                    "安装后校验失败：%s 中缺少 index.mjs 或 launcher.bat",
                    target_dir,
                )
                return False

            LOG.info("SnowLuma v%s 安装完成: %s", version, target_dir)
            return True

        except Exception as e:
            LOG.error("SnowLuma 安装失败: %s", e)
            return False

    @staticmethod
    def _resolve_payload_dir(extract_root: Path) -> Optional[Path]:
        """识别解压后的 payload 根目录。

        - 形态 A（顶层目录）::

              extract_root/
                SnowLuma-v1.7.5-win-x64/
                  index.mjs
                  launcher.bat
                  ...

          → 返回 ``extract_root/SnowLuma-v1.7.5-win-x64``。

        - 形态 B（散落文件，SnowLuma 实际形态）::

              extract_root/
                index.mjs
                launcher.bat
                node.exe
                ...

          → 返回 ``extract_root`` 本身。

        - 其它（空目录 / 多个无效顶层）→ ``None``。
        """
        entries = [p for p in extract_root.iterdir()]
        if not entries:
            return None

        # 标志性文件：SnowLuma 必含 launcher.bat + index.mjs
        def has_payload(d: Path) -> bool:
            return (d / "launcher.bat").is_file() and (d / "index.mjs").is_file()

        # 形态 B：直接散落
        if has_payload(extract_root):
            return extract_root

        # 形态 A：唯一顶层目录
        dirs = [e for e in entries if e.is_dir()]
        if len(dirs) == 1 and has_payload(dirs[0]):
            return dirs[0]

        # 退化：找第一个含 payload 的子目录
        for d in dirs:
            if has_payload(d):
                return d

        return None


__all__ = ["SnowLumaInstaller"]
