"""snowluma 命令组 — SnowLuma 管理与诊断（对标 ``ncatbot napcat``）。"""

from __future__ import annotations

import asyncio
import json

import click

from ..utils.colors import success, warning, info


def _get_manager():
    from ncatbot.utils import get_config_manager

    return get_config_manager()


def _get_snowluma_config():
    """从 ``adapters[]`` 中找到第一个 ``type=snowluma`` 的配置。

    返回 ``SnowLumaConfig`` 或 ``None``。
    """
    from ncatbot.adapter.snowluma.config import SnowLumaConfig

    mgr = _get_manager()
    for entry in mgr.config.adapters:
        if entry.type == "snowluma":
            return SnowLumaConfig.model_validate(entry.config or {})
    return None


# ============================================================
# snowluma 命令组
# ============================================================


@click.group()
def snowluma():
    """SnowLuma 管理"""


# ------------------------------------------------------------
# install
# ------------------------------------------------------------


@snowluma.command()
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    default=False,
    help="跳过确认，直接安装（CI / 脚本场景）",
)
@click.option(
    "--lite",
    is_flag=True,
    default=False,
    help="使用 SnowLuma-vX.Y.Z-win-x64-lite.zip（精简包）",
)
@click.option(
    "--install-dir",
    default=None,
    type=str,
    help="安装目录（默认 ./snowluma/）",
)
def install(yes: bool, lite: bool, install_dir: str | None):
    """下载并解压 SnowLuma（Windows x64）"""
    from ncatbot.adapter.snowluma.config import SnowLumaConfig
    from ncatbot.adapter.snowluma.setup.installer import SnowLumaInstaller
    from ncatbot.adapter.snowluma.setup.platform import (
        PlatformOps,
        UnsupportedPlatformError,
    )

    try:
        platform_ops = PlatformOps.create(install_dir=install_dir)
    except UnsupportedPlatformError as e:
        click.echo(click.style(str(e), fg="red"), err=True)
        raise SystemExit(1)

    cfg = SnowLumaConfig(use_lite_package=lite, install_dir=install_dir or "")
    installer = SnowLumaInstaller(platform_ops, snowluma_config=cfg)

    if platform_ops.is_snowluma_installed():
        click.echo(info(f"SnowLuma 已安装于: {platform_ops.snowluma_dir}"))
        if not yes and not click.confirm("是否仍要重新下载并覆盖?", default=False):
            return

    ok = installer.install(skip_confirm=yes)
    if ok:
        click.echo(success(f"SnowLuma 安装完成: {platform_ops.snowluma_dir}"))
        click.echo(
            info(
                "下一步: 启动 SnowLuma → 浏览器打开 http://localhost:5099 → "
                "在 OneBot v11 控制台启用 WebSocket 服务 → 扫码登录 QQ"
            )
        )
    else:
        click.echo(warning("SnowLuma 安装失败或被取消"), err=True)
        raise SystemExit(1)


# ------------------------------------------------------------
# stop
# ------------------------------------------------------------


@snowluma.command()
def stop():
    """提示停止 SnowLuma 进程（Windows 暂不支持自动 kill）"""
    import platform

    from ncatbot.adapter.snowluma.setup.platform import (
        PlatformOps,
        UnsupportedPlatformError,
    )

    try:
        platform_ops = PlatformOps.create()
    except UnsupportedPlatformError as e:
        click.echo(click.style(str(e), fg="red"), err=True)
        raise SystemExit(1)

    if platform.system() == "Windows":
        click.echo(
            warning(
                "Windows 下不支持按进程名停止 SnowLuma "
                "(可能误杀其它 node.exe 进程)，请手动关闭弹出的 cmd 窗口。"
            )
        )
        return

    platform_ops.stop_snowluma()
    click.echo(success("SnowLuma 停止指令已发送"))


# ------------------------------------------------------------
# diagnose
# ------------------------------------------------------------


@snowluma.group(invoke_without_command=True)
@click.pass_context
def diagnose(ctx: click.Context):
    """SnowLuma 诊断工具（WebSocket / WebUI）"""
    if ctx.invoked_subcommand is None:
        # 默认两项都跑一遍
        ctx.invoke(ws)
        click.echo()
        ctx.invoke(webui)


@diagnose.command("ws")
@click.option("--uri", default=None, help="WebSocket URI（默认读取配置）")
@click.option("--token", default=None, help="WebSocket Token（默认读取配置）")
def ws(uri: str | None, token: str | None):
    """检测 SnowLuma OneBot v11 WebSocket 连接"""
    cfg = _get_snowluma_config()
    final_uri = uri or (cfg.ws_uri if cfg else "ws://localhost:3001")
    final_token = token if token is not None else (cfg.ws_token if cfg else "")

    click.echo(
        info(
            f"测试 WebSocket 连接: {final_uri} (token={'***' if final_token else '<空>'})"
        )
    )

    asyncio.run(_check_ws(final_uri, final_token))


async def _check_ws(uri: str, token: str) -> None:
    """轻量 WS 探针 — 与 launcher.is_service_ok 等价但单独跑。"""
    import urllib.parse

    import websockets

    full_uri = uri
    if token:
        full_uri = f"{uri}?access_token={urllib.parse.quote(token, safe='')}"

    try:
        async with websockets.connect(full_uri, open_timeout=5) as conn:
            click.echo(success("✔ WebSocket 握手成功"))
            try:
                raw = await asyncio.wait_for(conn.recv(), timeout=2.0)
                data = json.loads(raw)
                if data.get("status") == "failed":
                    click.echo(
                        warning(
                            f"  服务器返回失败: retcode={data.get('retcode')} "
                            f"message={data.get('message')}"
                        )
                    )
                else:
                    self_id = data.get("self_id") or data.get("data", {}).get("self_id")
                    if self_id:
                        click.echo(success(f"  当前登录 QQ: {self_id}"))
                    else:
                        click.echo(
                            info(f"  收到首帧 (post_type={data.get('post_type')})")
                        )
            except asyncio.TimeoutError:
                click.echo(
                    info(
                        "  WS 连接成功但 2s 内无事件下发 (SnowLuma 未登录或心跳间隔较长)"
                    )
                )
    except Exception as e:
        click.echo(click.style(f"✘ WebSocket 连接失败: {e}", fg="red"), err=True)
        raise SystemExit(1)


@diagnose.command("webui")
@click.option("--uri", default=None, help="WebUI URI（默认读取配置）")
def webui(uri: str | None):
    """检测 SnowLuma WebUI 是否可达"""
    import httpx

    cfg = _get_snowluma_config()
    final_uri = uri or (cfg.webui_uri if cfg else "http://localhost:5099")

    click.echo(info(f"测试 WebUI 可达性: {final_uri}"))

    try:
        resp = httpx.get(final_uri, follow_redirects=True, timeout=5)
        if resp.status_code in (200, 301, 302, 304):
            click.echo(success(f"✔ WebUI 响应 {resp.status_code}"))
        else:
            click.echo(
                warning(f"WebUI 响应 {resp.status_code}（仍可能可用，请浏览器确认）")
            )
    except Exception as e:
        click.echo(click.style(f"✘ WebUI 不可达: {e}", fg="red"), err=True)
        raise SystemExit(1)


# ------------------------------------------------------------
# version
# ------------------------------------------------------------


@snowluma.command()
def version():
    """打印当前安装的 SnowLuma 版本与最新版本"""
    from ncatbot.adapter.snowluma.setup.installer import SnowLumaInstaller
    from ncatbot.adapter.snowluma.setup.platform import (
        PlatformOps,
        UnsupportedPlatformError,
    )

    try:
        platform_ops = PlatformOps.create()
    except UnsupportedPlatformError as e:
        click.echo(click.style(str(e), fg="red"), err=True)
        raise SystemExit(1)

    if platform_ops.is_snowluma_installed():
        installed = platform_ops.get_installed_version() or "(未知)"
        click.echo(info(f"已安装目录: {platform_ops.snowluma_dir}"))
        click.echo(info(f"package.json 版本: {installed}"))
    else:
        click.echo(warning(f"SnowLuma 未安装于: {platform_ops.snowluma_dir}"))

    latest = SnowLumaInstaller.get_latest_version()
    if latest:
        click.echo(info(f"GitHub 最新 release: v{latest}"))
    else:
        click.echo(warning("无法获取 GitHub 最新版本"))
