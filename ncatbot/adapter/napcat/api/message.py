"""消息操作 API Mixin"""

from typing import Any, Dict, Union


class MessageAPIMixin:

    async def send_private_msg(
        self, user_id: Union[str, int], message: list, **kwargs,
    ) -> dict:
        params: Dict[str, Any] = {"user_id": int(user_id), "message": message}
        params.update(kwargs)
        resp = await self._call("send_private_msg", params)
        return resp.get("data", {})

    async def send_group_msg(
        self, group_id: Union[str, int], message: list, **kwargs,
    ) -> dict:
        params: Dict[str, Any] = {"group_id": int(group_id), "message": message}
        params.update(kwargs)
        resp = await self._call("send_group_msg", params)
        return resp.get("data", {})

    async def delete_msg(self, message_id: Union[str, int]) -> None:
        await self._call("delete_msg", {"message_id": int(message_id)})

    async def send_forward_msg(
        self,
        message_type: str,
        target_id: Union[str, int],
        messages: list,
        **kwargs,
    ) -> dict:
        params: Dict[str, Any] = {
            "message_type": message_type,
            "messages": messages,
        }
        if message_type == "group":
            params["group_id"] = int(target_id)
        else:
            params["user_id"] = int(target_id)
        params.update(kwargs)
        resp = await self._call("send_forward_msg", params)
        return resp.get("data", {})
