"""
NapCat IBotAPI 实现

组合所有 Mixin 并提供 _call / _call_data 入口。
"""

from __future__ import annotations

from typing import Any, Optional, Union, TYPE_CHECKING

from ncatbot.api.interface import IBotAPI
from ncatbot.utils import get_log

from .message import MessageAPIMixin
from .group import GroupAPIMixin
from .account import AccountAPIMixin
from .query import QueryAPIMixin
from .file import FileAPIMixin

if TYPE_CHECKING:
    from ncatbot.adapter.napcat.connection.protocol import OB11Protocol

LOG = get_log("NapCatBotAPI")


class NapCatBotAPI(
    MessageAPIMixin,
    GroupAPIMixin,
    AccountAPIMixin,
    QueryAPIMixin,
    FileAPIMixin,
    IBotAPI,
):
    """NapCat 平台的 IBotAPI 实现"""

    def __init__(self, protocol: "OB11Protocol"):
        self._protocol = protocol

    async def _call(self, action: str, params: Optional[dict] = None) -> dict:
        return await self._protocol.call(action, params)

    async def _call_data(self, action: str, params: Optional[dict] = None) -> Any:
        resp = await self._call(action, params)
        return resp.get("data")

    # ---- 辅助功能 ----

    async def send_like(self, user_id: Union[str, int], times: int = 1) -> None:
        await self._call("send_like", {"user_id": int(user_id), "times": times})

    async def send_poke(
        self, group_id: Union[str, int], user_id: Union[str, int],
    ) -> None:
        await self._call("group_poke", {
            "group_id": int(group_id), "user_id": int(user_id),
        })
