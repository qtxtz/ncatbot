"""
Registrar — 无状态操作集合

提供 .on() 装饰器用于标记 handler + 附加 hooks。
flush_pending() 将待注册的 handler 批量注册到 Dispatcher。

提供 on_message / on_notice / on_request 等便捷装饰器。
"""

from typing import Any, Callable, Dict, List, Optional, TYPE_CHECKING

from ncatbot.utils import get_log
from .hook import Hook
from .builtin_hooks import MessageTypeFilter, SelfFilter

if TYPE_CHECKING:
    from .dispatcher import Dispatcher

LOG = get_log("Registrar")

# 全局 pending 队列
_pending_handlers: List[Callable] = []


class Registrar:
    """
    无状态操作集合

    .on() 装饰器:
    - 将默认 hooks setattr 到 func.__hooks__
    - 标记 func.__handler_meta__ 元信息
    - 加入 _pending_handlers 全局队列

    .fork() 创建带不同默认 hooks 的新 Registrar
    """

    def __init__(self, default_hooks: Optional[List[Hook]] = None):
        self._default_hooks = list(default_hooks or [])

    def on(
        self,
        event_type: str,
        priority: int = 0,
        **metadata: Any,
    ) -> Callable:
        """注册 handler 的装饰器"""

        def decorator(func: Callable) -> Callable:
            # 附加默认 hooks
            if not hasattr(func, "__hooks__"):
                func.__hooks__ = []
            for hook in self._default_hooks:
                if hook not in func.__hooks__:
                    func.__hooks__.append(hook)

            # 标记元信息
            func.__handler_meta__ = {
                "event_type": event_type,
                "priority": priority,
                **metadata,
            }

            _pending_handlers.append(func)
            return func

        return decorator

    def fork(
        self,
        extra_hooks: Optional[List[Hook]] = None,
        remove_hooks: Optional[List[Hook]] = None,
    ) -> "Registrar":
        """创建带不同默认 hooks 的新 Registrar"""
        new_hooks = [
            h for h in self._default_hooks if h not in (remove_hooks or [])
        ]
        new_hooks.extend(extra_hooks or [])
        return Registrar(default_hooks=new_hooks)

    # ==================== 便捷装饰器 ====================

    def on_group_message(
        self, priority: int = 0, **metadata: Any
    ) -> Callable:
        """注册群消息 handler (通过 BEFORE_CALL Hook 过滤 message_type)"""

        def decorator(func: Callable) -> Callable:
            if not hasattr(func, "__hooks__"):
                func.__hooks__ = []
            func.__hooks__.append(MessageTypeFilter("group"))
            return self.on(
                "ncatbot.message_event", priority=priority, **metadata
            )(func)

        return decorator

    def on_private_message(
        self, priority: int = 0, **metadata: Any
    ) -> Callable:
        """注册私聊消息 handler (通过 BEFORE_CALL Hook 过滤 message_type)"""

        def decorator(func: Callable) -> Callable:
            if not hasattr(func, "__hooks__"):
                func.__hooks__ = []
            func.__hooks__.append(MessageTypeFilter("private"))
            return self.on(
                "ncatbot.message_event", priority=priority, **metadata
            )(func)

        return decorator

    def on_message(self, priority: int = 0, **metadata: Any) -> Callable:
        """注册所有消息 handler (群+私聊)"""
        return self.on(
            "ncatbot.message_event", priority=priority, **metadata
        )

    def on_message_sent(
        self, priority: int = 0, **metadata: Any
    ) -> Callable:
        """注册消息发送 handler"""
        return self.on(
            "ncatbot.message_sent_event", priority=priority, **metadata
        )

    def on_notice(self, priority: int = 0, **metadata: Any) -> Callable:
        """注册通知事件 handler"""
        return self.on(
            "ncatbot.notice_event", priority=priority, **metadata
        )

    def on_request(self, priority: int = 0, **metadata: Any) -> Callable:
        """注册请求事件 handler"""
        return self.on(
            "ncatbot.request_event", priority=priority, **metadata
        )

    def on_meta(self, priority: int = 0, **metadata: Any) -> Callable:
        """注册元事件 handler"""
        return self.on(
            "ncatbot.meta_event", priority=priority, **metadata
        )

    def on_startup(self, priority: int = 0, **metadata: Any) -> Callable:
        """注册启动事件 handler (lifecycle connect)"""
        return self.on(
            "ncatbot.startup", priority=priority, **metadata
        )

    def on_heartbeat(self, priority: int = 0, **metadata: Any) -> Callable:
        """注册心跳事件 handler"""
        return self.on(
            "ncatbot.heartbeat", priority=priority, **metadata
        )


def flush_pending(dispatcher: "Dispatcher", plugin_name: str) -> int:
    """将待注册的 handler 批量注册到 Dispatcher

    Args:
        dispatcher: Dispatcher 实例
        plugin_name: 插件名称

    Returns:
        注册的 handler 数量
    """
    count = 0
    for func in _pending_handlers:
        meta = dict(func.__handler_meta__)  # copy 避免修改原始
        event_type = meta.pop("event_type")
        priority = meta.pop("priority", 0)

        dispatcher.register_handler(
            event_type=event_type,
            func=func,
            priority=priority,
            plugin_name=plugin_name,
            **meta,
        )
        count += 1

    _pending_handlers.clear()
    if count:
        LOG.debug(f"flush_pending({plugin_name}): 注册 {count} 个 handler")
    return count


# 全局默认 Registrar 实例
registrar = Registrar()
