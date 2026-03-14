"""
异步事件分发器

替代旧的 EventBus + BusEvent 设计。
只携带数据模型，handler 签名: async def handler(data: BaseEventData, api: IBotAPI) -> None
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from typing import (
    Awaitable,
    Callable,
    Dict,
    List,
    Optional,
    TYPE_CHECKING,
)

from ncatbot.utils import get_log

if TYPE_CHECKING:
    from ncatbot.api.interface import IBotAPI
    from ncatbot.types import BaseEventData

LOG = get_log("AsyncEventDispatcher")

# 哨兵值：handler 返回此值表示停止传播
STOP_PROPAGATION = object()

EventHandler = Callable[["BaseEventData", "IBotAPI"], Awaitable[Optional[object]]]


@dataclass
class HandlerEntry:
    name: str
    handler: EventHandler
    priority: int = 0
    timeout: float = 30.0
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])


class AsyncEventDispatcher:
    """异步事件分发器

    按 event_type（如 "message.group"、"notice.group_increase"）路由到注册的 handler。
    """

    def __init__(self, api: "IBotAPI"):
        self._api = api
        self._handlers: Dict[str, List[HandlerEntry]] = {}

    def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
        priority: int = 0,
        timeout: float = 30.0,
        name: Optional[str] = None,
    ) -> str:
        """注册事件处理器，返回 handler id"""
        entry = HandlerEntry(
            name=name or handler.__qualname__,
            handler=handler,
            priority=priority,
            timeout=timeout,
        )
        self._handlers.setdefault(event_type, []).append(entry)
        return entry.id

    def unsubscribe(self, handler_id: str) -> bool:
        """取消注册"""
        for entries in self._handlers.values():
            for entry in entries:
                if entry.id == handler_id:
                    entries.remove(entry)
                    return True
        return False

    async def dispatch(self, data: "BaseEventData") -> None:
        """分发数据模型到匹配的 handler"""
        event_type = self._resolve_type(data)
        handlers = self._collect_handlers(event_type)

        for entry in sorted(handlers, key=lambda h: -h.priority):
            try:
                result = await asyncio.wait_for(
                    entry.handler(data, self._api),
                    timeout=entry.timeout,
                )
                if result is STOP_PROPAGATION:
                    break
            except asyncio.TimeoutError:
                LOG.warning(f"Handler {entry.name} 超时")
            except Exception as e:
                LOG.error(f"Handler {entry.name} 异常: {e}", exc_info=True)

    def _collect_handlers(self, event_type: str) -> List[HandlerEntry]:
        """收集匹配的 handler（精确匹配 + 前缀匹配）"""
        result: List[HandlerEntry] = []

        # 精确匹配
        if event_type in self._handlers:
            result.extend(self._handlers[event_type])

        # 前缀匹配（如 "message" 匹配 "message.group"）
        parts = event_type.split(".")
        if len(parts) > 1:
            prefix = parts[0]
            if prefix in self._handlers:
                result.extend(self._handlers[prefix])

        return result

    @staticmethod
    def _resolve_type(data: "BaseEventData") -> str:
        """从数据模型推导事件类型字符串

        例:
          post_type=message, message_type=group → "message.group"
          post_type=notice, notice_type=group_increase → "notice.group_increase"
          post_type=request, request_type=friend → "request.friend"
          post_type=meta_event, meta_event_type=heartbeat → "meta_event.heartbeat"
        """
        post_type = getattr(data, "post_type", "")
        if hasattr(post_type, "value"):
            post_type = post_type.value

        # 根据 post_type 获取二级键
        secondary_key_map = {
            "message": "message_type",
            "message_sent": "message_type",
            "notice": "notice_type",
            "request": "request_type",
            "meta_event": "meta_event_type",
        }

        attr_name = secondary_key_map.get(post_type, "")
        secondary = ""
        if attr_name:
            val = getattr(data, attr_name, "")
            secondary = val.value if hasattr(val, "value") else str(val) if val else ""

            # notice 的 notify 子类型需要进一步细分
            if post_type == "notice" and secondary == "notify":
                sub = getattr(data, "sub_type", "")
                secondary = sub.value if hasattr(sub, "value") else str(sub) if sub else secondary

        if secondary:
            return f"{post_type}.{secondary}"
        return str(post_type)
