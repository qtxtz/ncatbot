from __future__ import annotations

from ncatbot.types import MetaEventData, MetaEventType

from .base import BaseEvent

__all__ = [
    "MetaEvent",
]


class MetaEvent(BaseEvent):
    """元事件实体"""

    _data: MetaEventData

    # ---- MetaEventData 字段 ----

    @property
    def meta_event_type(self) -> MetaEventType:
        return self._data.meta_event_type
