"""
系统与辅助功能 Mixin

包含点赞、戳一戳、AI 功能、能力查询、OCR、版本信息、退出等。
"""

from __future__ import annotations

from typing import Optional, Union

from ._base import NapCatBotAPIBase


class SystemMixin(NapCatBotAPIBase):
    """系统、辅助与 AI 相关 API"""

    # ------ 辅助功能 ------

    async def send_like(self, user_id: Union[str, int], times: int = 1) -> None:
        await self._call(
            "send_like",
            {"user_id": int(user_id), "times": times},
        )

    async def send_poke(
        self,
        user_id: Union[str, int],
        group_id: Optional[Union[str, int]] = None,
    ) -> None:
        if group_id:
            await self._call(
                "group_poke",
                {"group_id": int(group_id), "user_id": int(user_id)},
            )
        else:
            await self._call(
                "friend_poke",
                {"user_id": int(user_id)},
            )

    # ------ AI 功能 ------

    async def get_ai_characters(
        self, group_id: Union[str, int], chat_type: int
    ) -> list:
        return (
            await self._call_data(
                "get_ai_characters",
                {"group_id": int(group_id), "chat_type": chat_type},
            )
            or []
        )

    async def get_ai_record(
        self, group_id: Union[str, int], character_id: str, text: str
    ) -> str:
        data = await self._call_data(
            "get_ai_record",
            {"group_id": int(group_id), "character": character_id, "text": text},
        )
        return data or ""

    # ------ 能力查询与系统 ------

    async def can_send_image(self) -> bool:
        data = await self._call_data("can_send_image")
        return (data or {}).get("yes", False)

    async def can_send_record(self, group_id: Union[str, int]) -> bool:
        data = await self._call_data(
            "can_send_record", {"group_id": int(group_id)}
        )
        return (data or {}).get("yes", False)

    async def ocr_image(self, image: str) -> list:
        return await self._call_data("ocr_image", {"image": image}) or []

    async def get_version_info(self) -> dict:
        return await self._call_data("get_version_info") or {}

    async def bot_exit(self) -> None:
        await self._call("bot_exit")
