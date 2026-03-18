"""Push 事件实体"""

from __future__ import annotations

from typing import Any, List, TYPE_CHECKING

from ncatbot.event.common.base import BaseEvent
from ncatbot.event.common.mixins import HasSender

if TYPE_CHECKING:
    from ncatbot.types.github.events import GitHubPushEventData

__all__ = [
    "GitHubPushEvent",
]


class GitHubPushEvent(BaseEvent, HasSender):
    """GitHub Push 事件"""

    _data: "GitHubPushEventData"

    @property
    def user_id(self) -> str:
        return self._data.sender.user_id or ""

    @property
    def sender(self) -> Any:
        return self._data.sender

    @property
    def ref(self) -> str:
        return self._data.ref

    @property
    def before(self) -> str:
        return self._data.before

    @property
    def after(self) -> str:
        return self._data.after

    @property
    def commits(self) -> List[Any]:
        return self._data.commits

    @property
    def head_commit(self) -> Any:
        return self._data.head_commit

    @property
    def repo(self) -> str:
        return self._data.repo.full_name
