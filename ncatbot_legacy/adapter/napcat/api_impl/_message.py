"""
消息操作 Mixin

包含发送/接收/转发消息、表情回应、戳一戳、音乐分享等。
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union

from ._base import NapCatBotAPIBase


class MessageMixin(NapCatBotAPIBase):
    """消息相关 API"""

    async def send_private_msg(
        self, user_id: Union[str, int], message: list, **kwargs
    ) -> dict:
        message = await self._preupload_message(message)
        params: Dict[str, Any] = {"user_id": int(user_id), "message": message}
        params.update(kwargs)
        resp = await self._call("send_private_msg", params)
        return resp.get("data", {})

    async def send_group_msg(
        self, group_id: Union[str, int], message: list, **kwargs
    ) -> dict:
        message = await self._preupload_message(message)
        params: Dict[str, Any] = {"group_id": int(group_id), "message": message}
        params.update(kwargs)
        resp = await self._call("send_group_msg", params)
        return resp.get("data", {})

    async def delete_msg(self, message_id: Union[str, int]) -> None:
        await self._call("delete_msg", {"message_id": int(message_id)})

    async def send_forward_msg(
        self,
        group_id: Optional[Union[str, int]] = None,
        user_id: Optional[Union[str, int]] = None,
        messages: Optional[list] = None,
        news: Optional[List[str]] = None,
        prompt: Optional[str] = None,
        summary: Optional[str] = None,
        source: Optional[str] = None,
    ) -> dict:
        params: Dict[str, Any] = {}
        if messages is not None:
            params["messages"] = messages
        if news is not None:
            params["news"] = news
        if prompt is not None:
            params["prompt"] = prompt
        if summary is not None:
            params["summary"] = summary
        if source is not None:
            params["source"] = source
        if group_id is not None:
            params["group_id"] = int(group_id)
        elif user_id is not None:
            params["user_id"] = int(user_id)
        resp = await self._call("send_forward_msg", params)
        return resp.get("data", {})

    async def set_msg_emoji_like(
        self,
        message_id: Union[str, int],
        emoji_id: Union[str, int],
        set: bool = True,
    ) -> None:
        await self._call(
            "set_msg_emoji_like",
            {"message_id": str(message_id), "emoji_id": int(emoji_id), "set": set},
        )

    async def forward_group_single_msg(
        self, group_id: Union[str, int], message_id: Union[str, int]
    ) -> None:
        await self._call(
            "forward_group_single_msg",
            {"group_id": int(group_id), "message_id": int(message_id)},
        )

    async def forward_private_single_msg(
        self, user_id: Union[str, int], message_id: Union[str, int]
    ) -> None:
        await self._call(
            "forward_private_single_msg",
            {"user_id": int(user_id), "message_id": int(message_id)},
        )

    async def send_group_forward_msg(
        self,
        group_id: Union[str, int],
        messages: List[dict],
        news: List[str],
        prompt: str,
        summary: str,
        source: str,
    ) -> dict:
        resp = await self._call(
            "send_group_forward_msg",
            {
                "group_id": int(group_id),
                "messages": messages,
                "news": news,
                "prompt": prompt,
                "summary": summary,
                "source": source,
            },
        )
        return resp.get("data", {})

    async def send_private_forward_msg(
        self,
        user_id: Union[str, int],
        messages: List[dict],
        news: List[str],
        prompt: str,
        summary: str,
        source: str,
    ) -> dict:
        resp = await self._call(
            "send_private_forward_msg",
            {
                "user_id": int(user_id),
                "messages": messages,
                "news": news,
                "prompt": prompt,
                "summary": summary,
                "source": source,
            },
        )
        return resp.get("data", {})

    async def get_group_msg_history(
        self,
        group_id: Union[str, int],
        message_seq: Optional[Union[str, int]] = None,
        count: int = 20,
        reverse_order: bool = False,
    ) -> list:
        data: Dict[str, Any] = {
            "group_id": int(group_id),
            "count": count,
            "reverseOrder": reverse_order,
        }
        if message_seq is not None:
            data["message_seq"] = message_seq
        result = await self._call_data("get_group_msg_history", data)
        return (result or {}).get("messages", [])

    async def get_friend_msg_history(
        self,
        user_id: Union[str, int],
        message_seq: Union[str, int],
        count: int = 20,
        reverse_order: bool = False,
    ) -> list:
        result = await self._call_data(
            "get_friend_msg_history",
            {
                "user_id": int(user_id),
                "message_seq": message_seq,
                "count": count,
                "reverseOrder": reverse_order,
            },
        )
        return (result or {}).get("messages", [])

    async def get_record(
        self,
        file: Optional[str] = None,
        file_id: Optional[str] = None,
        out_format: str = "mp3",
    ) -> dict:
        return (
            await self._call_data(
                "get_record",
                {"file": file, "file_id": file_id, "out_format": out_format},
            )
            or {}
        )

    async def get_image(
        self,
        file: Optional[str] = None,
        file_id: Optional[str] = None,
    ) -> dict:
        return (
            await self._call_data(
                "get_image", {"file": file, "file_id": file_id}
            )
            or {}
        )

    async def fetch_emoji_like(
        self,
        message_id: Union[str, int],
        emoji_id: Union[str, int],
        emoji_type: Union[str, int],
    ) -> dict:
        return (
            await self._call_data(
                "fetch_emoji_like",
                {
                    "message_id": message_id,
                    "emojiId": emoji_id,
                    "emojiType": emoji_type,
                },
            )
            or {}
        )

    async def group_poke(
        self, group_id: Union[str, int], user_id: Union[str, int]
    ) -> None:
        await self._call(
            "group_poke",
            {"group_id": int(group_id), "user_id": int(user_id)},
        )

    async def friend_poke(self, user_id: Union[str, int]) -> None:
        await self._call("friend_poke", {"user_id": int(user_id)})

    async def send_group_music(
        self,
        group_id: Union[str, int],
        type: str,
        id: Union[int, str],
    ) -> dict:
        message = [{"type": "music", "data": {"type": type, "id": str(id)}}]
        return await self.send_group_msg(group_id, message)

    async def send_group_custom_music(
        self,
        group_id: Union[str, int],
        url: str,
        title: str,
        image: str,
        audio: Optional[str] = None,
        content: Optional[str] = None,
    ) -> dict:
        data: Dict[str, Any] = {
            "type": "custom",
            "url": url,
            "title": title,
            "image": image,
        }
        if audio is not None:
            data["audio"] = audio
        if content is not None:
            data["content"] = content
        message = [{"type": "music", "data": data}]
        return await self.send_group_msg(group_id, message)

    async def send_private_music(
        self,
        user_id: Union[str, int],
        type: str,
        id: Union[int, str],
    ) -> dict:
        message = [{"type": "music", "data": {"type": type, "id": str(id)}}]
        return await self.send_private_msg(user_id, message)

    async def send_private_custom_music(
        self,
        user_id: Union[str, int],
        url: str,
        title: str,
        image: str,
        audio: Optional[str] = None,
        content: Optional[str] = None,
    ) -> dict:
        data: Dict[str, Any] = {
            "type": "custom",
            "url": url,
            "title": title,
            "image": image,
        }
        if audio is not None:
            data["audio"] = audio
        if content is not None:
            data["content"] = content
        message = [{"type": "music", "data": data}]
        return await self.send_private_msg(user_id, message)
