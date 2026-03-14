"""
NapCat 启动编排

替代旧的 environment.py + nc_service.py，
统一管理本地/远程模式的启动流程。
"""

import asyncio
import json
import time
from typing import Optional

import websockets

from ncatbot.utils import NcatBotError, get_log, ncatbot_config
from .auth import AuthHandler, LoginStatus
from .config import NapCatConfig
from .installer import NapCatInstaller
from .platform import PlatformOps, UnsupportedPlatformError

LOG = get_log("NapCatLauncher")


class NapCatLauncher:
    """NapCat 启动编排"""

    def __init__(self):
        self._platform: Optional[PlatformOps] = None
        self._installer: Optional[NapCatInstaller] = None
        self._config: Optional[NapCatConfig] = None

    @property
    def platform(self) -> PlatformOps:
        if self._platform is None:
            self._platform = PlatformOps.create()
        return self._platform

    def _ensure_components(self) -> None:
        if self._installer is None:
            self._installer = NapCatInstaller(self.platform)
        if self._config is None:
            self._config = NapCatConfig(self.platform)

    # ==================== WebSocket 连接测试 ====================

    @staticmethod
    async def _test_websocket(report_status: bool = False) -> bool:
        uri = ncatbot_config.get_uri_with_token()
        try:
            async with websockets.connect(uri, open_timeout=5) as ws:
                data = json.loads(await ws.recv())
                if data.get("status") == "failed":
                    retcode = data.get("retcode")
                    message = data.get("message", "未知错误")
                    if retcode == 1403:
                        raise NcatBotError("WebSocket Token 填写错误", False)
                    raise NcatBotError(f"WebSocket 连接失败: {message}", False)
                return True
        except NcatBotError:
            raise
        except Exception as e:
            if report_status:
                LOG.warning(f"测试 WebSocket 连接失败: {e}")
            return False

    async def is_service_ok(self, timeout: int = 0, show_info: bool = True) -> bool:
        if timeout == 0:
            return bool(await self._test_websocket(show_info))

        expire_time = time.time() + timeout
        while True:
            if await self.is_service_ok(show_info=(time.time() > expire_time)):
                return True
            if time.time() > expire_time:
                return False
            await asyncio.sleep(0.5)

    async def wait_for_service(self, timeout: int = 60) -> None:
        if not await self.is_service_ok(timeout):
            raise NcatBotError("连接 NapCat WebSocket 服务器超时")
        LOG.info("连接 NapCat WebSocket 服务器成功!")

    # ==================== 远程模式 ====================

    async def _check_remote_service(self) -> bool:
        if not await self.is_service_ok():
            LOG.info("NapCat 服务器离线或未登录")
            return False

        LOG.info(
            f"NapCat 服务器 {ncatbot_config.napcat.ws_uri} 在线, 正在检查账号状态..."
        )

        if not ncatbot_config.napcat.enable_webui:
            LOG.warning(
                f"跳过基于 WebUI 交互的检查, "
                f"请自行确保 NapCat 已登录正确的 QQ {ncatbot_config.bot_uin}"
            )
            return True

        status = AuthHandler().report_status()

        if status == LoginStatus.OK:
            return True
        elif status == LoginStatus.ABNORMAL:
            LOG.error("登录状态异常, 请检查远端 NapCat 服务")
            raise NcatBotError("登录状态异常, 请检查远端 NapCat 服务")
        elif status == LoginStatus.UIN_MISMATCH:
            LOG.error("远端登录的 QQ 与配置的 QQ 号不匹配")
            raise NcatBotError("登录的 QQ 号与配置的 QQ 号不匹配")

        return False

    async def _launch_remote(self) -> None:
        LOG.info("正在以远端模式运行, 检查中...")
        if not await self._check_remote_service():
            raise NcatBotError("远端 NapCat 服务异常, 请检查远端服务或关闭远端模式")

    # ==================== 本地模式 ====================

    async def _launch_local(self) -> None:
        LOG.info("正在以本地模式运行, 检查中...")

        if await self.is_service_ok():
            if await self._check_remote_service():
                LOG.debug("NapCat 服务正常")
                return

        try:
            _ = self.platform
        except UnsupportedPlatformError:
            raise NcatBotError("本地模式不支持该操作系统, 请使用远端模式")

        self._ensure_components()

        if not self._installer.ensure_installed():
            raise NcatBotError("安装或更新 NapCat 失败")

        self._config.configure_all()
        self.platform.start_napcat(str(ncatbot_config.bot_uin))

        await self._handle_login()

    async def _handle_login(self) -> None:
        nc = ncatbot_config.napcat

        if nc.enable_webui:
            if not await self.is_service_ok(3):
                LOG.info("登录中...")
                AuthHandler().login()
                await self.wait_for_service()
                LOG.info("连接成功")
            else:
                LOG.info("快速登录成功, 跳过登录引导")
        else:
            timeout = ncatbot_config.websocket_timeout
            if not await self.is_service_ok(timeout):
                raise TimeoutError(
                    f"NapCat 未能在 {timeout} 秒内启动, WebSocket 连接失败"
                )

    # ==================== 主入口 ====================

    async def launch(self) -> None:
        """启动 NapCat 服务（根据配置选择模式）"""
        if ncatbot_config.napcat.remote_mode:
            await self._launch_remote()
        else:
            await self._launch_local()
