"""
Dispatcher — 纯机械分发器

订阅 EventBus，分发事件到已注册的 handlers。
不含任何 Session 逻辑（Session 完全通过 Hook 实现）。

与 ncatbot/core/client/dispatcher.py (EventDispatcher) 不同:
- EventDispatcher: BaseEvent → NcatBotEvent → 发布到 EventBus
- Dispatcher (本文件): 从 EventBus 接收 → 分发到 handler 函数
"""

import asyncio
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

from ncatbot.utils import get_log

from .hook import Hook, HookAction, HookContext, HookStage, get_hooks

if TYPE_CHECKING:
    from ncatbot.core.client.event_bus import EventBus
    from ncatbot.core.client.ncatbot_event import NcatBotEvent

LOG = get_log("Dispatcher")


@dataclass
class HandlerEntry:
    """已注册的 handler 条目"""

    func: Callable
    event_type: str
    priority: int = 0
    plugin_name: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class Dispatcher:
    """
    纯机械分发器

    - 订阅 EventBus 上的所有 ncatbot 事件
    - 收集匹配的 handlers
    - 对每个 handler: BEFORE_CALL hooks → 执行 → AFTER_CALL hooks
    - revoke_plugin() 支持热重载精确清理
    """

    def __init__(self, event_bus: "EventBus"):
        self._handlers: Dict[str, List[HandlerEntry]] = {}  # event_type → handlers
        self._event_bus = event_bus

        # 订阅所有 ncatbot 事件
        self._subscription_id = event_bus.subscribe(
            "re:ncatbot\\..*",
            self._on_event,
            priority=-1,  # 低优先级，让 EventRegistry 的直接订阅先执行
        )

    # ==================== Handler 管理 ====================

    def register_handler(
        self,
        event_type: str,
        func: Callable,
        priority: int = 0,
        plugin_name: str = "",
        **metadata: Any,
    ) -> HandlerEntry:
        """注册 handler 到分发器"""
        entry = HandlerEntry(
            func=func,
            event_type=event_type,
            priority=priority,
            plugin_name=plugin_name,
            metadata=metadata,
        )

        if event_type not in self._handlers:
            self._handlers[event_type] = []

        self._handlers[event_type].append(entry)
        # 按优先级降序排序
        self._handlers[event_type].sort(key=lambda e: -e.priority)

        LOG.debug(
            f"注册 handler: {func.__name__} → {event_type} "
            f"(priority={priority}, plugin={plugin_name})"
        )
        return entry

    def unregister_handler(self, entry: HandlerEntry) -> bool:
        """移除单个 handler"""
        handlers = self._handlers.get(entry.event_type, [])
        try:
            handlers.remove(entry)
            if not handlers:
                del self._handlers[entry.event_type]
            return True
        except ValueError:
            return False

    def revoke_plugin(self, plugin_name: str) -> int:
        """热重载用: 移除该插件的所有 handler，返回移除数量"""
        removed = 0
        for event_type in list(self._handlers.keys()):
            original_len = len(self._handlers[event_type])
            self._handlers[event_type] = [
                e
                for e in self._handlers[event_type]
                if e.plugin_name != plugin_name
            ]
            removed += original_len - len(self._handlers[event_type])
            if not self._handlers[event_type]:
                del self._handlers[event_type]

        if removed:
            LOG.info(f"revoke_plugin({plugin_name}): 移除 {removed} 个 handler")
        return removed

    # ==================== 核心分发 ====================

    async def _on_event(self, ncatbot_event: "NcatBotEvent") -> None:
        """EventBus 回调: 纯机械分发"""
        event = ncatbot_event.data
        event_type = ncatbot_event.type

        # snapshot 防止并发修改
        handlers = self._collect_handlers(event_type)

        for entry in handlers:
            if getattr(event, "_propagation_stopped", False):
                break

            ctx = HookContext(
                event=event,
                event_type=event_type,
                handler_entry=entry,
            )

            # --- BEFORE_CALL hooks ---
            before_hooks = get_hooks(entry.func, HookStage.BEFORE_CALL)
            skip = False
            for hook in before_hooks:
                try:
                    action = await hook.execute(ctx)
                    if action == HookAction.SKIP:
                        skip = True
                        break
                except Exception as e:
                    LOG.exception(
                        f"BEFORE_CALL hook {hook} 执行异常 "
                        f"(handler={entry.func.__name__}): {e}"
                    )
                    skip = True
                    break
            if skip:
                continue

            # --- 执行 handler ---
            try:
                result = await self._execute(entry, event, **ctx.kwargs)
                ctx.result = result

                # --- AFTER_CALL hooks ---
                after_hooks = get_hooks(entry.func, HookStage.AFTER_CALL)
                for hook in after_hooks:
                    try:
                        await hook.execute(ctx)
                    except Exception as e:
                        LOG.exception(
                            f"AFTER_CALL hook {hook} 执行异常 "
                            f"(handler={entry.func.__name__}): {e}"
                        )

            except Exception as e:
                ctx.error = e
                # --- ON_ERROR hooks ---
                error_hooks = get_hooks(entry.func, HookStage.ON_ERROR)
                handled = False
                for hook in error_hooks:
                    try:
                        await hook.execute(ctx)
                        handled = True
                    except Exception as hook_err:
                        LOG.exception(
                            f"ON_ERROR hook {hook} 自身异常: {hook_err}"
                        )
                if not handled:
                    LOG.exception(
                        f"Handler {entry.func.__name__} 执行异常: {e}"
                    )

    def _collect_handlers(self, event_type: str) -> List[HandlerEntry]:
        """收集匹配的 handlers (snapshot)"""
        # 精确匹配
        result = list(self._handlers.get(event_type, []))

        # 前缀匹配 (如 ncatbot.notice_event 也触发 ncatbot.notice)
        parts = event_type.split(".")
        for i in range(len(parts) - 1, 0, -1):
            prefix = ".".join(parts[:i])
            result.extend(self._handlers.get(prefix, []))

        result.sort(key=lambda e: -e.priority)
        return result

    @staticmethod
    async def _execute(
        entry: HandlerEntry, event: Any, **kwargs: Any
    ) -> Any:
        """执行 handler，注入 plugin 实例 (如果是方法) + kwargs"""
        func = entry.func
        plugin = entry.metadata.get("plugin_instance")

        if plugin:
            if asyncio.iscoroutinefunction(func):
                return await func(plugin, event, **kwargs)
            else:
                return await asyncio.to_thread(func, plugin, event, **kwargs)
        else:
            if asyncio.iscoroutinefunction(func):
                return await func(event, **kwargs)
            else:
                return await asyncio.to_thread(func, event, **kwargs)

    # ==================== 查询 ====================

    def get_handlers(self, event_type: str) -> List[HandlerEntry]:
        """获取指定事件类型的 handlers"""
        return list(self._handlers.get(event_type, []))

    def get_all_handlers(self) -> Dict[str, List[HandlerEntry]]:
        """获取所有 handlers"""
        return {k: list(v) for k, v in self._handlers.items()}

    def shutdown(self) -> None:
        """关闭 dispatcher"""
        self._event_bus.unsubscribe(self._subscription_id)
        self._handlers.clear()
        LOG.info("Dispatcher 已关闭")
