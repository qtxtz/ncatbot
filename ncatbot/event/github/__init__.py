"""GitHub 平台专用事件实体"""

from .issue import GitHubIssueEvent, GitHubIssueCommentEvent
from .pr import GitHubPREvent, GitHubPRReviewCommentEvent
from .push import GitHubPushEvent
from .misc import GitHubStarEvent, GitHubForkEvent, GitHubReleaseEvent
from .factory import create_github_entity

# 自动注册 GitHub 平台工厂和 secondary keys 到通用工厂
from ncatbot.event.common.factory import (
    register_platform_factory as _register,
    register_platform_secondary_keys as _register_keys,
)

_register("github", create_github_entity)
_register_keys(
    "github",
    {
        "issue": "action",
        "pull_request": "action",
        "comment": "action",
        "star": "action",
        "release": "action",
    },
)
del _register, _register_keys

__all__ = [
    # issue
    "GitHubIssueEvent",
    "GitHubIssueCommentEvent",
    # pr
    "GitHubPREvent",
    "GitHubPRReviewCommentEvent",
    # push
    "GitHubPushEvent",
    # misc
    "GitHubStarEvent",
    "GitHubForkEvent",
    "GitHubReleaseEvent",
    # factory
    "create_github_entity",
]
