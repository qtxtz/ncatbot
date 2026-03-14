from __future__ import annotations

from pydantic import Field

from .base import BaseEventData
from .enums import MetaEventType, PostType
from .misc import Status

__all__ = [
    "MetaEventData",
    "LifecycleMetaEventData",
    "HeartbeatMetaEventData",
]


class MetaEventData(BaseEventData):
    post_type: PostType = Field(default=PostType.META_EVENT)
    meta_event_type: MetaEventType


class LifecycleMetaEventData(MetaEventData):
    meta_event_type: MetaEventType = Field(default=MetaEventType.LIFECYCLE)
    sub_type: str = Field(default="enable")


class HeartbeatMetaEventData(MetaEventData):
    meta_event_type: MetaEventType = Field(default=MetaEventType.HEARTBEAT)
    status: Status
    interval: int
