from __future__ import annotations

from typing import TYPE_CHECKING

from ncatbot.types import BaseEventData, PostType

if TYPE_CHECKING:
    from ncatbot.api.interface import IBotAPI

__all__ = [
    "BaseEvent",
]


class BaseEvent:
    """事件实体基类 — 包装数据模型 + API，提供行为方法

    插件代码可直接访问 event.user_id / event.message 等，
    通过显式 @property 暴露底层数据模型字段。
    """

    __slots__ = ("_data", "_api")

    def __init__(self, data: BaseEventData, api: IBotAPI) -> None:
        self._data = data
        self._api = api

    # ---- 底层访问 ----

    @property
    def api(self) -> IBotAPI:
        return self._api

    @property
    def data(self) -> BaseEventData:
        """获取底层纯数据模型（可序列化）"""
        return self._data

    # ---- BaseEventData 字段 ----

    @property
    def time(self) -> int:
        return self._data.time

    @property
    def self_id(self) -> str:
        return self._data.self_id

    @property
    def post_type(self) -> PostType:
        return self._data.post_type

    def __repr__(self) -> str:
        return f"{type(self).__name__}(data={self._data!r})"
