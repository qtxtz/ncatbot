"""SnowLuma 平台操作抽象层。

与 ``napcat.setup.platform`` 同构 — 提供 Windows/Linux/macOS 工厂入口和
启动 / 停止 / 安装目录查询。当前仅完整支持 **Windows x64**（用户在 Q4 中
明确选择 UAC 提权启动）；Linux/macOS 留接口但抛 ``UnsupportedPlatformError``。

Windows 启动方式：
- ``ShellExecuteW("runas", cmd.exe, /c cd /d <dir> && launcher.bat)`` 弹出 UAC，
  在独立的管理员进程中启动 ``node ./index.mjs``。
- NcatBot 进程退出后 SnowLuma 仍继续运行（与 napcat 行为一致）。
"""

from __future__ import annotations

import json
import platform as _platform
import subprocess
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

if sys.platform == "win32":
    import ctypes

from ncatbot.utils import get_log

from ..constants import WINDOWS_SNOWLUMA_DIR

LOG = get_log("SnowLumaPlatform")


class UnsupportedPlatformError(Exception):
    """当前操作系统不被 SnowLuma 自动启动流程支持。"""

    def __init__(self, system: Optional[str] = None) -> None:
        system = system or _platform.system()
        super().__init__(f"不支持的操作系统: {system}")


class PlatformOps(ABC):
    """平台操作抽象基类。"""

    def __init__(self, install_dir: Optional[str] = None) -> None:
        # install_dir 允许由配置覆盖；空字符串/None 走平台默认
        self._install_dir_override = install_dir or None

    @staticmethod
    def create(install_dir: Optional[str] = None) -> "PlatformOps":
        system = _platform.system()
        if system == "Windows":
            return WindowsOps(install_dir=install_dir)
        if system == "Linux":
            return LinuxOps(install_dir=install_dir)
        raise UnsupportedPlatformError(system)

    # ------------------------- 通用属性 -------------------------

    @property
    @abstractmethod
    def snowluma_dir(self) -> Path:
        """SnowLuma 安装目录绝对路径。"""

    @property
    def config_dir(self) -> Path:
        """SnowLuma 配置目录（``<dir>/config/``）。"""
        return self.snowluma_dir / "config"

    @property
    def runtime_config_path(self) -> Path:
        """``config/runtime.json``。"""
        return self.config_dir / "runtime.json"

    @property
    def webui_config_path(self) -> Path:
        """``config/webui.json``。"""
        return self.config_dir / "webui.json"

    @property
    def launcher_script(self) -> Path:
        """启动脚本/可执行入口。"""
        return self.snowluma_dir / "launcher.bat"

    # ------------------------- 状态查询 -------------------------

    def is_snowluma_installed(self) -> bool:
        """判定标准：目录存在且 ``index.mjs`` 与 ``launcher.bat`` 都在。"""
        d = self.snowluma_dir
        return (d / "index.mjs").exists() and self.launcher_script.exists()

    def get_installed_version(self) -> Optional[str]:
        """从 ``package.json`` 中读取版本号；SnowLuma 当前版本为 ``0.1.0``
        （runtime distribution manifest 内部版本），实际版本由目录名 / 上层
        installer 维护。读不到时返回 ``None``。"""
        package_json = self.snowluma_dir / "package.json"
        if not package_json.exists():
            return None
        try:
            with open(package_json, "r", encoding="utf-8") as f:
                return json.load(f).get("version")
        except (json.JSONDecodeError, KeyError, OSError):
            return None

    @abstractmethod
    def is_snowluma_running(self) -> bool:
        """SnowLuma 进程是否在运行。"""

    @abstractmethod
    def start_snowluma(self) -> None:
        """启动 SnowLuma（带 UAC / 独立进程）。"""

    @abstractmethod
    def stop_snowluma(self) -> None:
        """停止 SnowLuma 进程。"""


# ============================================================
# Windows 实现
# ============================================================


class WindowsOps(PlatformOps):
    """Windows x64 平台操作 — 通过 UAC 提权运行 ``launcher.bat``。"""

    @property
    def snowluma_dir(self) -> Path:
        if self._install_dir_override:
            return Path(self._install_dir_override).resolve()
        return Path(WINDOWS_SNOWLUMA_DIR).resolve()

    def is_snowluma_running(self) -> bool:
        """通过 ``tasklist`` 粗判 ``node.exe`` 是否在跑。

        SnowLuma 自带 ``node.exe`` 启动，但宿主机可能存在其它 Node 进程，因此
        此处只能粗略判断；精确判定通过 WebSocket / WebUI 探针完成（在
        ``SnowLumaLauncher`` 中以连通性为准，与 napcat 一致）。
        """
        try:
            result = subprocess.run(
                ["tasklist", "/FI", "IMAGENAME eq node.exe", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return "node.exe" in result.stdout
        except Exception:
            return False

    def start_snowluma(self) -> None:
        launcher_path = self.launcher_script
        if not launcher_path.exists():
            raise FileNotFoundError(
                f"找不到 SnowLuma 启动脚本: {launcher_path}\n"
                f"请先运行 `ncatbot snowluma install` 或检查 install_dir 配置。"
            )

        LOG.info("正在 UAC 提权启动 SnowLuma: %s", launcher_path)

        # ShellExecuteW + runas → 弹出 UAC 对话框，独立管理员进程中执行
        # cd /d 切到工作目录，再调用 launcher.bat（一行: node ./index.mjs）
        ret = ctypes.windll.shell32.ShellExecuteW(
            None,  # hwnd
            "runas",  # lpOperation: 请求管理员权限
            "cmd.exe",  # lpFile
            f'/c cd /d "{self.snowluma_dir}" && "{launcher_path}"',
            None,  # lpDirectory
            1,  # nShowCmd: SW_SHOWNORMAL
        )
        if ret <= 32:
            raise RuntimeError(
                f"UAC 提权启动失败 (错误码={ret})。"
                f"请以管理员身份运行 NcatBot，或手动执行: {launcher_path}"
            )

    def stop_snowluma(self) -> None:
        # SnowLuma 是普通 node.exe 进程，直接 kill 风险大（会误伤其它 Node）。
        # 与 napcat Windows 行为对齐，仅给出提示，不主动结束。
        LOG.warning(
            "Windows 下不支持按进程名停止 SnowLuma "
            "(可能误杀其它 node.exe 进程)。请手动关闭弹出的 cmd 窗口。"
        )


# ============================================================
# Linux / macOS 占位实现
# ============================================================


class LinuxOps(PlatformOps):
    """Linux 占位实现 — release 提供 ``-linux-x64.tar.gz``，但本阶段未实现。"""

    @property
    def snowluma_dir(self) -> Path:
        if self._install_dir_override:
            return Path(self._install_dir_override).resolve()
        return Path.home() / ".snowluma"

    def is_snowluma_running(self) -> bool:
        raise UnsupportedPlatformError(
            "Linux 平台的 SnowLuma 自动启动尚未实现，请使用 skip_setup: true 手动管理。"
        )

    def start_snowluma(self) -> None:
        raise UnsupportedPlatformError(
            "Linux 平台的 SnowLuma 自动启动尚未实现，请使用 skip_setup: true 手动管理。"
        )

    def stop_snowluma(self) -> None:
        raise UnsupportedPlatformError(
            "Linux 平台的 SnowLuma 自动启动尚未实现。"
        )


__all__ = [
    "PlatformOps",
    "WindowsOps",
    "LinuxOps",
    "UnsupportedPlatformError",
]
