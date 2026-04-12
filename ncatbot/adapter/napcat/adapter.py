"""
NapCat 适配器主类

纯编排类，组合 setup / connection / api / parser 子组件。
"""

import logging
from typing import Any, Dict, Optional


from ..base import BaseAdapter
from ncatbot.api import IAPIClient
from ncatbot.utils import get_config_manager, get_log
from ncatbot.utils import NapCatConfig
from ncatbot.utils import resolve_event_log_level, format_event_summary

from .api.bot_api import NapCatBotAPI
from .connection.protocol import OB11Protocol
from .connection.websocket import NapCatWebSocket
from .parser import NapCatEventParser
from .setup.launcher import NapCatLauncher

LOG = get_log("NapCatAdapter")


class NapCatAdapter(BaseAdapter):
    name = "napcat"
    description = "NapCat (OneBot v11) 适配器"
    supported_protocols = ["onebot_v11"]
    platform = "qq"

    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        *,
        bot_uin: str = "",
        websocket_timeout: int = 15,
    ):
        super().__init__(
            config=config,
            bot_uin=bot_uin,
            websocket_timeout=websocket_timeout,
        )
        self._config = NapCatConfig.model_validate(self._raw_config)
        self._launcher = NapCatLauncher(
            napcat_config=self._config,
            bot_uin=self._bot_uin,
            websocket_timeout=self._websocket_timeout,
        )
        self._ws: Optional[NapCatWebSocket] = None
        self._protocol: Optional[OB11Protocol] = None
        self._api: Optional[NapCatBotAPI] = None
        self._parser = NapCatEventParser()

    @property
    def napcat_config(self) -> NapCatConfig:
        """适配器的 NapCat 配置（供外部诊断工具访问）。"""
        return self._config

    async def setup(self) -> None:
        await self._launcher.launch()

    async def connect(self) -> None:
        uri = self._config.get_uri_with_token()
        self._ws = NapCatWebSocket(uri)
        await self._ws.connect()
        self._protocol = OB11Protocol(self._ws)
        self._api = NapCatBotAPI(self._protocol)
        self._protocol.set_event_handler(self._on_event)

    async def disconnect(self) -> None:
        if self._protocol:
            self._protocol.cancel_all()
        if self._ws:
            await self._ws.disconnect()
        self._api = self._protocol = self._ws = None

    def stop_managed_runtime(self) -> None:
        """停止由 NapCat 平台层管理的本地运行时。"""
        self._launcher.stop()

    @classmethod
    def cli_configure(cls) -> Dict[str, Any]:
        import click

        click.echo(click.style("\n— NapCat 适配器配置 —", fg="cyan", bold=True))

        # 询问是否自动下载安装 NapCat
        auto_install = click.confirm("是否现在自动下载并安装 NapCat?", default=False)
        if auto_install:
            cls._cli_install_napcat()
            # 自动安装模式：启动时由 configure_all() 自动配置，使用默认值
            click.echo(
                click.style(
                    "  将使用默认连接参数，适配器启动时自动配置",
                    dim=True,
                )
            )
            return {
                "ws_uri": "ws://localhost:3001",
                "ws_token": "napcat_ws",
                "webui_uri": "http://localhost:6099",
                "webui_token": "napcat_webui",
                "enable_webui": True,
            }

        ws_uri = click.prompt("WebSocket 地址", default="ws://localhost:3001")
        ws_token = click.prompt("WebSocket Token", default="napcat_ws")
        webui_uri = click.prompt("WebUI 地址", default="http://localhost:6099")
        webui_token = click.prompt("WebUI Token", default="napcat_webui")
        enable_webui = click.confirm("启用 WebUI?", default=True)
        return {
            "ws_uri": ws_uri,
            "ws_token": ws_token,
            "webui_uri": webui_uri,
            "webui_token": webui_token,
            "enable_webui": enable_webui,
        }

    @staticmethod
    def _cli_install_napcat() -> None:
        """CLI 环境下安装 NapCat。"""
        import click

        try:
            from .setup.platform import PlatformOps, UnsupportedPlatformError
            from .setup.installer import NapCatInstaller

            try:
                platform_ops = PlatformOps.create()
            except UnsupportedPlatformError:
                click.echo(click.style("当前操作系统不支持自动安装 NapCat", fg="red"))
                return

            installer = NapCatInstaller(platform_ops)
            ok = installer.install(skip_confirm=True)
            if ok:
                click.echo(click.style("NapCat 安装成功!", fg="green"))
            else:
                click.echo(click.style("NapCat 安装失败，请稍后手动安装", fg="red"))
        except Exception as e:
            click.echo(click.style(f"安装过程出错: {e}", fg="red"))

    async def listen(self) -> None:
        await self._ws.listen(self._protocol.on_message)

    def get_api(self) -> IAPIClient:
        return self._api

    @property
    def connected(self) -> bool:
        return self._ws is not None and self._ws.connected

    async def _on_event(self, raw_data: dict) -> None:
        """收到事件推送，解析为数据模型后回调给分发器"""
        data_model = self._parser.parse(raw_data)
        if data_model is None:
            return

        # 根据配置决定事件日志级别
        event_type = data_model.resolve_type()
        logging_config = get_config_manager().config.logging
        log_level = resolve_event_log_level(event_type, logging_config.event_log_levels)

        if log_level is not None:
            if logging_config.event_log_format == "summary":
                summary = format_event_summary(raw_data)
                LOG._log(log_level, summary, (), {})
                # DEBUG 级别额外输出完整 JSON
                s = data_model.model_dump_json()
                if len(s) > 2000:
                    s = s[:2000] + "..."
                LOG._log(
                    logging.DEBUG, f"收到事件 {data_model.post_type.value}: {s}", (), {}
                )
            else:
                # raw 模式：旧行为
                s = data_model.model_dump_json()
                if len(s) > 2000:
                    s = s[:2000] + "..."
                LOG._log(
                    log_level, f"收到事件 {data_model.post_type.value}: {s}", (), {}
                )

        if self._event_callback:
            await self._event_callback(data_model)
