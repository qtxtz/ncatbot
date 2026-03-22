"""
Bilibili API 查询方法单元测试

规范:
  BQ-01: parse_bili_id 匹配 BV 号
  BQ-02: parse_bili_id 匹配 av 号
  BQ-03: parse_bili_id 匹配 b23 短链（mock 重定向）
  BQ-04: parse_bili_id 无匹配返回 None
  BQ-05: parse_bili_id 从完整 URL 中提取 BV 号
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ncatbot.adapter.bilibili.api.query import QueryAPIMixin, _AV_PATTERN, _BV_PATTERN


class TestBiliIdRegex:
    """BQ-01/02: 正则匹配（纯同步）"""

    def test_bq01_bv_pattern_standard(self):
        """BQ-01: 标准 BV 号匹配"""
        m = _BV_PATTERN.search("BV1wa411Q7N6")
        assert m is not None
        assert m.group(1) == "1wa411Q7N6"

    def test_bq01_bv_pattern_in_url(self):
        """BQ-01: URL 中的 BV 号"""
        m = _BV_PATTERN.search(
            "https://www.bilibili.com/video/BV1MdAgziEdg/?spm_id_from=333"
        )
        assert m is not None
        assert m.group(1) == "1MdAgziEdg"

    def test_bq01_bv_case_insensitive(self):
        """BQ-01: bv 小写前缀"""
        m = _BV_PATTERN.search("bv1wa411Q7N6 some text")
        assert m is not None

    def test_bq02_av_pattern(self):
        """BQ-02: 标准 av 号匹配"""
        m = _AV_PATTERN.search("av258296202")
        assert m is not None
        assert m.group(1) == "258296202"

    def test_bq02_av_in_text(self):
        """BQ-02: 混合文本中的 av 号"""
        m = _AV_PATTERN.search("快去看 AV12345 这个视频")
        assert m is not None
        assert m.group(1) == "12345"

    def test_bq04_no_match(self):
        """BQ-04: 无匹配"""
        assert _BV_PATTERN.search("没有B站链接") is None
        assert _AV_PATTERN.search("没有B站链接") is None


class _FakeQueryMixin(QueryAPIMixin):
    """为测试提供 _credential 属性的 Mixin 子类"""

    def __init__(self):
        self._credential = None


class TestParseBiliId:
    """BQ-01~05: parse_bili_id 异步方法"""

    @pytest.fixture
    def mixin(self):
        return _FakeQueryMixin()

    @pytest.mark.asyncio
    async def test_bq01_parse_bv(self, mixin):
        """BQ-01: parse_bili_id 匹配 BV 号"""
        result = await mixin.parse_bili_id("BV1wa411Q7N6")
        assert result is not None
        assert result.id_type == "bv"
        assert result.bvid == "BV1wa411Q7N6"
        assert result.video_id == "BV1wa411Q7N6"

    @pytest.mark.asyncio
    async def test_bq02_parse_av(self, mixin):
        """BQ-02: parse_bili_id 匹配 av 号"""
        result = await mixin.parse_bili_id("av258296202")
        assert result is not None
        assert result.id_type == "av"
        assert result.aid == 258296202
        assert result.video_id == "av258296202"

    @pytest.mark.asyncio
    async def test_bq04_parse_no_match(self, mixin):
        """BQ-04: parse_bili_id 无匹配返回 None"""
        result = await mixin.parse_bili_id("没有任何B站链接的文本")
        assert result is None

    @pytest.mark.asyncio
    async def test_bq05_parse_full_url(self, mixin):
        """BQ-05: parse_bili_id 从完整 URL 中提取 BV 号"""
        result = await mixin.parse_bili_id(
            "https://www.bilibili.com/video/BV1MdAgziEdg/?spm_id_from=333.1387.homepage.video_card.click"
        )
        assert result is not None
        assert result.id_type == "bv"
        assert result.bvid == "BV1MdAgziEdg"

    @pytest.mark.asyncio
    async def test_bq03_parse_b23_mock(self, mixin):
        """BQ-03: parse_bili_id 匹配 b23 短链（mock 重定向）"""
        mock_resp = MagicMock()
        mock_resp.url = "https://www.bilibili.com/video/BV1wa411Q7N6?p=1"

        mock_session_ctx = AsyncMock()
        mock_session_ctx.__aenter__ = AsyncMock(return_value=mock_resp)
        mock_session_ctx.__aexit__ = AsyncMock(return_value=False)

        mock_session = MagicMock()
        mock_session.head = MagicMock(return_value=mock_session_ctx)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=False)

        with patch("aiohttp.ClientSession", return_value=mock_session):
            result = await mixin.parse_bili_id("看这个 https://b23.tv/abcdef 太好看了")

        assert result is not None
        assert result.id_type == "bv"
        assert result.bvid == "BV1wa411Q7N6"
        assert (
            result.redirected_url == "https://www.bilibili.com/video/BV1wa411Q7N6?p=1"
        )
