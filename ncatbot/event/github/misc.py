"""Star / Fork / Release 事件实体"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from ncatbot.event.common.base import BaseEvent
from ncatbot.event.common.mixins import HasSender

if TYPE_CHECKING:
    from ncatbot.types.github.events import (
        GitHubStarEventData,
        GitHubForkEventData,
        GitHubReleaseEventData,
    )
    from ncatbot.types.github.models import GitHubForkee, GitHubRelease

__all__ = [
    "GitHubStarEvent",
    "GitHubForkEvent",
    "GitHubReleaseEvent",
]


class GitHubStarEvent(BaseEvent, HasSender):
    """GitHub Star 事件"""

    _data: "GitHubStarEventData"

    @property
    def user_id(self) -> str:
        return self._data.sender.user_id or ""

    @property
    def sender(self) -> Any:
        return self._data.sender

    @property
    def repo(self) -> str:
        return self._data.repo.full_name

    @property
    def starred_at(self) -> str:
        return self._data.starred_at


class GitHubForkEvent(BaseEvent, HasSender):
    """GitHub Fork 事件"""

    _data: "GitHubForkEventData"

    @property
    def user_id(self) -> str:
        return self._data.sender.user_id or ""

    @property
    def sender(self) -> Any:
        return self._data.sender

    @property
    def repo(self) -> str:
        return self._data.repo.full_name

    @property
    def forkee(self) -> "GitHubForkee":
        return self._data.forkee

    @property
    def forkee_full_name(self) -> str:
        return self._data.forkee.full_name


class GitHubReleaseEvent(BaseEvent, HasSender):
    """GitHub Release 事件"""

    _data: "GitHubReleaseEventData"

    @property
    def user_id(self) -> str:
        return self._data.sender.user_id or ""

    @property
    def sender(self) -> Any:
        return self._data.sender

    @property
    def repo(self) -> str:
        return self._data.repo.full_name

    @property
    def release(self) -> "GitHubRelease":
        return self._data.release

    @property
    def release_tag(self) -> str:
        return self._data.release.tag_name

    @property
    def release_name(self) -> str:
        return self._data.release.name

    @property
    def release_body(self) -> str:
        return self._data.release.body

    @property
    def prerelease(self) -> bool:
        return self._data.release.prerelease
