"""查询操作 API Mixin"""

from __future__ import annotations

import re
from typing import Optional

from ncatbot.types.bilibili.models import ParsedBiliId, VideoInfo
from ncatbot.utils import get_log

LOG = get_log("QueryAPI")

_BV_PATTERN = re.compile(r"[bB][vV]([1-9A-HJ-NP-Za-km-z]{10})")
_AV_PATTERN = re.compile(r"[aA][vV](\d+)")
_B23_PATTERN = re.compile(r"https?://b23\.tv/\S+")


class QueryAPIMixin:
    async def get_user_info(self, user_id: int) -> dict:
        from bilibili_api import user as bili_user

        u = bili_user.User(uid=user_id, credential=self._credential)
        return await u.get_user_info()

    async def get_video_info(self, video_id: str) -> Optional[VideoInfo]:
        """获取B站视频信息。

        Parameters
        ----------
        video_id:
            BV 号（如 ``BV1wa411Q7N6``）或 av 号（如 ``av258296202``）。
        """
        from bilibili_api import video as bili_video

        if video_id.lower().startswith("av"):
            v = bili_video.Video(aid=int(video_id[2:]), credential=self._credential)
        else:
            v = bili_video.Video(bvid=video_id, credential=self._credential)
        raw = await v.get_info()
        return VideoInfo.from_raw(raw)

    async def parse_bili_id(self, text: str) -> Optional[ParsedBiliId]:
        """从文本中解析B站视频 ID。

        支持 b23.tv 短链（自动重定向）、BV 号、av 号。
        返回 ``ParsedBiliId`` 或 ``None``（无法匹配时）。
        """
        import aiohttp

        raw_text = text

        # 1. 尝试匹配 b23 短链
        b23_match = _B23_PATTERN.search(text)
        if b23_match:
            short_url = b23_match.group(0)
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.head(
                        short_url,
                        allow_redirects=True,
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as resp:
                        text = str(resp.url)
                        LOG.info("b23 重定向: %s -> %s", short_url, text)
            except Exception as e:
                LOG.warning("b23 重定向失败 %s: %s", short_url, e)
                return None

        # 2. 匹配 BV 号
        bv_match = _BV_PATTERN.search(text)
        if bv_match:
            bvid = "BV" + bv_match.group(1)
            return ParsedBiliId(
                id_type="bv",
                bvid=bvid,
                raw_url=raw_text,
                redirected_url=text if b23_match else "",
            )

        # 3. 匹配 av 号
        av_match = _AV_PATTERN.search(text)
        if av_match:
            aid = int(av_match.group(1))
            return ParsedBiliId(
                id_type="av",
                aid=aid,
                raw_url=raw_text,
                redirected_url=text if b23_match else "",
            )

        return None
