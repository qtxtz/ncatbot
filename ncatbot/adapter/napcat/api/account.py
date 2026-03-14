"""账号操作 API Mixin"""


class AccountAPIMixin:

    async def set_friend_add_request(
        self, flag: str, approve: bool = True, remark: str = "",
    ) -> None:
        await self._call("set_friend_add_request", {
            "flag": flag, "approve": approve, "remark": remark,
        })

    async def set_group_add_request(
        self, flag: str, sub_type: str, approve: bool = True, reason: str = "",
    ) -> None:
        await self._call("set_group_add_request", {
            "flag": flag, "sub_type": sub_type,
            "approve": approve, "reason": reason,
        })
