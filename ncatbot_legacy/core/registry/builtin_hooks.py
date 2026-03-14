"""
内置 Hook 集合

提供常用的 BEFORE_CALL 过滤 Hook，用于事件类型筛选等。
"""

from typing import Optional

from .hook import Hook, HookAction, HookContext, HookStage


class MessageTypeFilter(Hook):
    """过滤消息类型 (group / private)"""

    stage = HookStage.BEFORE_CALL

    def __init__(self, message_type: str, *, priority: int = 100):
        self.message_type = message_type
        self.priority = priority

    async def execute(self, ctx: HookContext) -> HookAction:
        event = ctx.event
        if getattr(event, "message_type", None) != self.message_type:
            return HookAction.SKIP
        return HookAction.CONTINUE

    def __repr__(self) -> str:
        return f"<MessageTypeFilter(type={self.message_type})>"


class PostTypeFilter(Hook):
    """过滤 post_type (message / notice / request / meta_event)"""

    stage = HookStage.BEFORE_CALL

    def __init__(self, post_type: str, *, priority: int = 100):
        self.post_type = post_type
        self.priority = priority

    async def execute(self, ctx: HookContext) -> HookAction:
        event = ctx.event
        if getattr(event, "post_type", None) != self.post_type:
            return HookAction.SKIP
        return HookAction.CONTINUE

    def __repr__(self) -> str:
        return f"<PostTypeFilter(type={self.post_type})>"


class SubTypeFilter(Hook):
    """过滤 sub_type"""

    stage = HookStage.BEFORE_CALL

    def __init__(self, sub_type: str, *, priority: int = 100):
        self.sub_type = sub_type
        self.priority = priority

    async def execute(self, ctx: HookContext) -> HookAction:
        event = ctx.event
        if getattr(event, "sub_type", None) != self.sub_type:
            return HookAction.SKIP
        return HookAction.CONTINUE

    def __repr__(self) -> str:
        return f"<SubTypeFilter(type={self.sub_type})>"


class SelfFilter(Hook):
    """过滤掉自身发送的消息"""

    stage = HookStage.BEFORE_CALL

    def __init__(self, *, priority: int = 200):
        self.priority = priority

    async def execute(self, ctx: HookContext) -> HookAction:
        event = ctx.event
        user_id = getattr(event, "user_id", None)
        self_id = getattr(event, "self_id", None)
        if user_id is not None and self_id is not None and user_id == self_id:
            return HookAction.SKIP
        return HookAction.CONTINUE

    def __repr__(self) -> str:
        return "<SelfFilter>"


# ==================== 预置实例 ====================

group_only = MessageTypeFilter("group")
private_only = MessageTypeFilter("private")
non_self = SelfFilter()
