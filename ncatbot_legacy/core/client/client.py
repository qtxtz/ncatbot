"""
Bot 客户端

组合各模块，提供统一的 Bot 客户端接口。
"""

from typing import List, Optional, Type, TypeVar, TYPE_CHECKING

from ncatbot.utils import get_log
from ncatbot.utils.error import NcatBotError
from ncatbot.core.api.interface import IBotAPI
from ncatbot.core.service import ServiceManager
from ncatbot.core.service.builtin import (
    PluginConfigService,
    FileWatcherService,
    PluginDataService,
    TimeTaskService,
)
from ncatbot.core.registry import RegistryEngine, HandlerDispatcher
from ncatbot.core.service.builtin import SessionManager
from ncatbot.adapter import BaseAdapter
from ncatbot.adapter.napcat import NapCatAdapter

from .event_bus import EventBus
from .dispatcher import EventDispatcher
from .lifecycle import LifecycleManager

if TYPE_CHECKING:
    from ncatbot.plugin_system import BasePlugin

T = TypeVar("T")
LOG = get_log("Client")


class BotClient(LifecycleManager):
    """
    Bot 客户端

    架构：
    ┌─────────────────────────────────────────────────────────┐
    │                       BotClient                         │
    │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐ │
    │  │ Services │  │ EventBus │  │ Registry │  │Lifecycle│ │
    │  │(服务层)   │ │(分发中心) │ │(注册接口)  │ │(生命周期)│ │
    │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬────┘ │
    │       │             │             │             │       │
    │       └─────────────┴─────────────┴─────────────┘       │
    │                         ↓                               │
    │                   EventDispatcher                       │
    │                    (解析 & 分发)                         │
    └─────────────────────────────────────────────────────────┘

    事件流：
    MessageRouter → Dispatcher → EventBus → Handlers/Plugins

    测试模式：
    使用 start(mock=True) 启动 Mock 模式，连接到 MockServer。
    事件注入通过 MockServer.inject_event() 等方法实现。
    """

    _initialized = False

    def __init__(self, adapter: Optional[BaseAdapter] = None):
        """
        初始化 Bot 客户端

        Args:
            adapter: 平台适配器实例。默认使用 NapCatAdapter。
        """
        if BotClient._initialized:
            raise NcatBotError("BotClient 实例只能创建一次")
        BotClient._initialized = True

        # 1. 核心组件
        self.event_bus = EventBus()

        # 2. 注册引擎 (legacy, 过渡期保留 — 用于命令系统和旧过滤器)
        self.registry_engine = RegistryEngine()

        # 3. Handler Dispatcher（Hook 驱动，新架构核心）
        self.handler_dispatcher = HandlerDispatcher(self.event_bus)

        # Legacy: RegistryEngine 仍需要消息和遗留事件路由
        self.event_bus.subscribe(
            "re:ncatbot\\.message_event|ncatbot\\.message_sent_event",
            self._on_message_for_registry,
            priority=0,
        )
        self.event_bus.subscribe(
            "re:ncatbot\\.notice_event|ncatbot\\.request_event|ncatbot\\.meta_event",
            self._on_legacy_for_registry,
            priority=0,
        )

        # 3. 服务管理器（注入 EventBus）
        self.services = ServiceManager(event_bus=self.event_bus)
        self.services.set_bot_client(self)  # 过渡期兼容

        # 4. 注册内置服务
        self.services.register(PluginConfigService)
        self.services.register(FileWatcherService)
        self.services.register(PluginDataService)
        self.services.register(TimeTaskService)
        self.services.register(SessionManager)

        # 5. 适配器
        self.adapter: BaseAdapter = adapter or NapCatAdapter()

        # 6. API（延迟绑定，在 adapter.connect() 后获取）
        self.api: Optional[IBotAPI] = None

        # 事件分发器（延迟初始化）
        self.dispatcher: Optional[EventDispatcher] = None

        # 生命周期管理器
        LifecycleManager.__init__(self, self.services, self.event_bus)

        # 注册内置处理器
        self._register_builtin_handlers()

    @classmethod
    def reset_singleton(cls):
        """
        重置单例状态（仅用于测试）

        允许在测试中创建新的 BotClient 实例。
        """
        cls._initialized = False

    async def _setup_api(self) -> None:
        """设置 API（在 adapter.connect() 后调用）"""
        from .dispatcher import EventDispatcher

        # 从适配器获取 IBotAPI
        self.api = self.adapter.get_api()

        # 创建事件分发器
        self.dispatcher = EventDispatcher(self.event_bus, self.api, services=self.services)

        # 将适配器的事件输出连接到分发器
        self.adapter.set_event_callback(self.dispatcher.dispatch)

        # 注入 BotClient 引用到 RegistryEngine（过渡期）
        self.registry_engine.set_bot_client(self)

    async def _on_message_for_registry(self, event) -> None:
        """EventBus 回调：消息事件 → RegistryEngine (legacy, 命令系统)"""
        await self.registry_engine.handle_message_event(event.data)

    async def _on_legacy_for_registry(self, event) -> None:
        """EventBus 回调：通知/请求/元事件 → RegistryEngine (legacy)"""
        await self.registry_engine.handle_legacy_event(event.data)

    def _register_builtin_handlers(self):
        """注册内置处理器"""
        from .ncatbot_event import NcatBotEvent

        async def _on_startup(event: NcatBotEvent):
            e = event.data
            LOG.info(f"Bot {e.self_id} 启动成功")

        self.event_bus.subscribe(
            "ncatbot.meta_event",
            _on_startup,
            priority=0,
        )

    # ==================== 工具方法 ====================

    def get_registered_plugins(self) -> List["BasePlugin"]:
        """获取已注册的插件列表"""
        if self.plugin_loader:
            return list(self.plugin_loader.plugins.values())
        return []

    def get_plugin(self, plugin_type: Type[T]) -> T:
        """获取指定类型的插件"""
        for plugin in self.get_registered_plugins():
            if isinstance(plugin, plugin_type):
                return plugin
        raise ValueError(f"插件 {plugin_type.__name__} 未找到")

    def get_plugin_class_by_name(self, plugin_name: str) -> Type["BasePlugin"]:
        """获取指定名称的插件类"""
        for plugin in self.get_registered_plugins():
            if plugin.name == plugin_name:
                return type(plugin)
        raise ValueError(f"插件 {plugin_name} 未找到")
