from __future__ import annotations

from ncatbot.types import MetaEventData

from .base import BaseEvent

__all__ = [
    "MetaEvent",
]


class MetaEvent(BaseEvent):
    """元事件实体"""

    _data: MetaEventData
