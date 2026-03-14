"""BotAPIClient — 对外暴露的胖客户端

高频 API 平铺在顶层，低频 API 按操作类型分到 manage / info / support。
"""

from __future__ import annotations

from typing import Any, Union

from ncatbot.api.interface import IBotAPI
from ncatbot.api._sugar import MessageSugarMixin
from ncatbot.api.extensions.manage import ManageExtension
from ncatbot.api.extensions.info import InfoExtension
from ncatbot.api.extensions.support import SupportExtension


class BotAPIClient(MessageSugarMixin):
    """插件开发者使用的 API 客户端

    高频操作直接调：
        await api.post_group_msg(group_id, text="hello")
        await api.delete_msg(message_id)

    低频操作走命名空间：
        await api.manage.set_group_ban(group_id, user_id, 600)
        await api.info.get_group_member_list(group_id)
        await api.support.upload_group_file(group_id, file, name)
    """

    def __init__(self, adapter_api: IBotAPI) -> None:
        self._base = adapter_api

        # 低频命名空间
        self.manage = ManageExtension(adapter_api)
        self.info = InfoExtension(adapter_api)
        self.support = SupportExtension(adapter_api)

    # ---- 高频原子 API（显式透传）----

    async def send_group_msg(
        self, group_id: Union[str, int], message: list, **kwargs: Any,
    ) -> dict:
        return await self._base.send_group_msg(group_id, message, **kwargs)

    async def send_private_msg(
        self, user_id: Union[str, int], message: list, **kwargs: Any,
    ) -> dict:
        return await self._base.send_private_msg(user_id, message, **kwargs)

    async def delete_msg(self, message_id: Union[str, int]) -> None:
        await self._base.delete_msg(message_id)

    async def send_forward_msg(
        self, message_type: str, target_id: Union[str, int],
        messages: list, **kwargs: Any,
    ) -> dict:
        return await self._base.send_forward_msg(
            message_type, target_id, messages, **kwargs,
        )

    async def send_poke(
        self, group_id: Union[str, int], user_id: Union[str, int],
    ) -> None:
        await self._base.send_poke(group_id, user_id)

    # ---- 兜底：未显式定义的方法代理到底层 ----

    def __getattr__(self, name: str) -> Any:
        return getattr(self._base, name)
