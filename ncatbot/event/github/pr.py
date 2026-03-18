"""Pull Request 事件实体"""

from __future__ import annotations

from typing import Any, TYPE_CHECKING

from ncatbot.event.common.base import BaseEvent
from ncatbot.event.common.mixins import Replyable, HasSender, Deletable

if TYPE_CHECKING:
    from ncatbot.api.github.interface import IGitHubAPIClient
    from ncatbot.types.github.events import (
        GitHubPREventData,
        GitHubPRReviewCommentEventData,
    )

__all__ = [
    "GitHubPREvent",
    "GitHubPRReviewCommentEvent",
]


class GitHubPREvent(BaseEvent, HasSender, Replyable):
    """GitHub Pull Request 事件"""

    _data: "GitHubPREventData"
    _api: "IGitHubAPIClient"

    @property
    def api(self) -> "IGitHubAPIClient":
        return self._api

    @property
    def user_id(self) -> str:
        return self._data.sender.user_id or ""

    @property
    def sender(self) -> Any:
        return self._data.sender

    @property
    def pr_number(self) -> int:
        return self._data.pr_number

    @property
    def pr_title(self) -> str:
        return self._data.pr_title

    @property
    def action(self) -> str:
        return self._data.action

    @property
    def repo(self) -> str:
        return self._data.repo.full_name

    @property
    def merged(self) -> bool:
        return self._data.merged

    async def reply(self, text: str, **kwargs: Any) -> Any:
        return await self._api.create_issue_comment(
            repo=self._data.repo.full_name,
            issue_number=self._data.pr_number,
            body=text,
        )


class GitHubPRReviewCommentEvent(BaseEvent, HasSender, Replyable, Deletable):
    """GitHub PR Review 评论事件"""

    _data: "GitHubPRReviewCommentEventData"
    _api: "IGitHubAPIClient"

    @property
    def api(self) -> "IGitHubAPIClient":
        return self._api

    @property
    def user_id(self) -> str:
        return self._data.sender.user_id or ""

    @property
    def sender(self) -> Any:
        return self._data.sender

    @property
    def comment_body(self) -> str:
        return self._data.comment_body

    @property
    def pr_number(self) -> int:
        return self._data.pr_number

    @property
    def path(self) -> str:
        return self._data.path

    @property
    def repo(self) -> str:
        return self._data.repo.full_name

    async def reply(self, text: str, **kwargs: Any) -> Any:
        return await self._api.create_issue_comment(
            repo=self._data.repo.full_name,
            issue_number=self._data.pr_number,
            body=text,
        )

    async def delete(self) -> Any:
        return await self._api.delete_comment(
            repo=self._data.repo.full_name,
            comment_id=int(self._data.comment_id),
        )
