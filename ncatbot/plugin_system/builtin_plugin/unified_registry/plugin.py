"""统一注册插件

仅负责事件订阅和委托给 UnifiedRegistryService。
"""

from typing import TYPE_CHECKING, Callable

from ncatbot.utils import get_log
from ...builtin_mixin import NcatBotPlugin

if TYPE_CHECKING:
    from ncatbot.core import NcatBotEvent

LOG = get_log("UnifiedRegistry")


class UnifiedRegistryPlugin(NcatBotPlugin):
    """统一注册插件

    仅订阅事件并委托给 UnifiedRegistryService 处理。
    """

    name = "UnifiedRegistryPlugin"
    author = "huan-yp"
    desc = "统一的过滤器和命令注册插件"
    version = "3.0.0"

    async def on_load(self) -> None:
        """插件加载时订阅事件"""
        self.event_bus.subscribe(
            "re:ncatbot.message_event|ncatbot.message_sent_event",
            self.handle_message_event,
            timeout=900,
        )
        self.event_bus.subscribe(
            "re:ncatbot.notice_event|ncatbot.request_event",
            self.handle_legacy_event,
            timeout=900,
        )
        self.event_bus.subscribe(
            "ncatbot.plugin_unload",
            self.handle_plugin_unload_event,
        )
        self.event_bus.subscribe(
            "ncatbot.plugin_load",
            self.handle_plugin_load_event,
        )

        # 初始化插件函数映射（用于找到函数所属的插件）
        self.func_plugin_map = {}

    @property
    def _service(self):
        """获取 UnifiedRegistryService"""
        return self.services.unified_registry

    async def handle_plugin_unload_event(self, event: "NcatBotEvent") -> None:
        """处理插件卸载事件"""
        LOG.debug(f"处理插件卸载事件: {event.data['name']}")
        self._service.handle_plugin_unload(event.data["name"])

    async def handle_plugin_load_event(self, event: "NcatBotEvent") -> None:
        """处理插件加载事件"""
        self._service.handle_plugin_load()

    async def handle_message_event(self, event: "NcatBotEvent") -> bool:
        """处理消息事件（委托给服务）"""
        await self._service.handle_message_event(
            event.data,
            self.event_bus,
            plugin_finder=self._find_plugin_for_function
        )

    async def handle_legacy_event(self, event: "NcatBotEvent") -> bool:
        """处理通知和请求事件（委托给服务）"""
        return await self._service.handle_legacy_event(
            event.data,
            plugin_finder=self._find_plugin_for_function
        )

    def _find_plugin_for_function(self, func: Callable) -> "NcatBotPlugin":
        """查找函数所属的插件"""
        if func in self.func_plugin_map:
            return self.func_plugin_map[func]

        plugins = self.list_plugins(obj=True)
        for plugin in plugins:
            plugin_class = plugin.__class__
            if func in plugin_class.__dict__.values():
                self.func_plugin_map[func] = plugin
                return plugin

        return None

    def clear(self):
        """清理缓存"""
        self.func_plugin_map.clear()
        self._service.clear()
