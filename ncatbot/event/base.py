from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ncatbot.types import BaseEventData

if TYPE_CHECKING:
    from ncatbot.api.interface import IBotAPI

__all__ = [
    "BaseEvent",
]


class BaseEvent:
    """事件实体基类 — 包装数据模型 + API，提供行为方法

    插件代码可直接访问 event.user_id / event.message 等，
    通过 __getattr__ 代理到底层数据模型。
    """

    __slots__ = ("_data", "_api")

    def __init__(self, data: BaseEventData, api: IBotAPI) -> None:
        self._data = data
        self._api = api

    def __getattr__(self, name: str) -> Any:
        try:
            return getattr(self._data, name)
        except AttributeError:
            raise AttributeError(
                f"'{type(self).__name__}' has no attribute '{name}'"
            ) from None

    @property
    def api(self) -> IBotAPI:
        return self._api

    @property
    def data(self) -> BaseEventData:
        """获取底层纯数据模型（可序列化）"""
        return self._data

    def __repr__(self) -> str:
        return f"{type(self).__name__}(data={self._data!r})"
