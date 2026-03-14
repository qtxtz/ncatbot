"""
账号操作 Mixin

包含请求处理、个人资料、在线状态、好友管理、消息已读标记等。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ._base import NapCatBotAPIBase


class AccountMixin(NapCatBotAPIBase):
    """账号与请求相关 API"""

    # ------ 请求处理 ------

    async def set_friend_add_request(
        self, flag: str, approve: bool = True, remark: Optional[str] = None
    ) -> None:
        params: Dict[str, Any] = {"flag": flag, "approve": approve}
        if remark is not None:
            params["remark"] = remark
        await self._call("set_friend_add_request", params)

    async def set_group_add_request(
        self,
        flag: str,
        sub_type: str,
        approve: bool = True,
        reason: str = "",
    ) -> None:
        await self._call(
            "set_group_add_request",
            {
                "flag": flag,
                "sub_type": sub_type,
                "approve": approve,
                "reason": reason,
            },
        )

    # ------ 个人资料 ------

    async def set_qq_profile(
        self, nickname: str, personal_note: str, sex: str
    ) -> None:
        sex_mapping = {"未知": 0, "男": 1, "女": 2}
        sex_id = str(sex_mapping.get(sex, 0))
        await self._call(
            "set_qq_profile",
            {"nickname": nickname, "personal_note": personal_note, "sex": sex_id},
        )

    async def set_online_status(
        self, status: int, ext_status: int, battery_status: int
    ) -> None:
        await self._call(
            "set_online_status",
            {"status": status, "ext_status": ext_status, "battery_status": battery_status},
        )

    async def set_qq_avatar(self, file: str) -> None:
        pass

    async def set_self_longnick(self, long_nick: str) -> None:
        await self._call("set_self_longnick", {"longNick": long_nick})

    async def get_status(self) -> dict:
        return await self._call_data("get_status") or {}

    # ------ 好友管理 ------

    async def get_friends_with_cat(self) -> List[dict]:
        return await self._call_data("get_friends_with_category") or []

    async def delete_friend(
        self, user_id: Union[str, int], block: bool = True, both: bool = True
    ) -> None:
        await self._call(
            "delete_friend",
            {"user_id": int(user_id), "block": block, "both": both},
        )

    async def set_friend_remark(
        self, user_id: Union[str, int], remark: str
    ) -> None:
        await self._call(
            "set_friend_remark",
            {"user_id": int(user_id), "remark": remark},
        )

    # ------ 消息已读 & 其他 ------

    async def mark_group_msg_as_read(self, group_id: Union[str, int]) -> None:
        await self._call("mark_group_msg_as_read", {"group_id": int(group_id)})

    async def mark_private_msg_as_read(self, user_id: Union[str, int]) -> None:
        await self._call("mark_private_msg_as_read", {"user_id": int(user_id)})

    async def create_collection(self, raw_data: str, brief: str) -> None:
        await self._call("create_collection", {"rawData": raw_data, "brief": brief})

    async def get_recent_contact(self) -> List[dict]:
        return await self._call_data("get_recent_contact") or []

    async def ask_share_group(self, group_id: Union[str, int]) -> None:
        await self._call("AskShareGroup", {"group_id": int(group_id)})

    async def fetch_custom_face(self, count: int = 48) -> list:
        return await self._call_data("fetch_custom_face", {"count": count}) or []

    async def nc_get_user_status(self, user_id: Union[str, int]) -> dict:
        return (
            await self._call_data("nc_get_user_status", {"user_id": int(user_id)})
            or {}
        )

    async def set_input_status(
        self, event_type: int, user_id: Union[str, int]
    ) -> None:
        await self._call(
            "set_input_status",
            {"event_type": event_type, "user_id": int(user_id)},
        )
