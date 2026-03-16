"""
14_external_api — 外部 API 集成

演示功能:
  - 异步 HTTP 请求 (aiohttp)
  - ConfigMixin 管理 API key / URL
  - @registrar.on_group_command() + str 参数绑定
  - 错误处理与优雅降级

使用方式:
  "每日一言"         → 调用一言 API 获取随机一句话
  "随机图片"         → 发送本地示例图片
  "设置一言源 xxx"   → 修改一言 API 地址
  "api状态"          → 查看 API 配置和状态
"""

from pathlib import Path

import aiohttp

from ncatbot.core import registrar
from ncatbot.event import GroupMessageEvent
from ncatbot.plugin import NcatBotPlugin
from ncatbot.utils import get_log

LOG = get_log("ExternalAPI")

PLUGIN_DIR = Path(__file__).parent
FALLBACK_IMAGE = PLUGIN_DIR / "resources" / "example.jpg"

# 默认的一言 API（免费公共 API）
DEFAULT_HITOKOTO_URL = "https://v1.hitokoto.cn"


class ExternalAPIPlugin(NcatBotPlugin):
    name = "external_api"
    version = "1.0.0"
    author = "NcatBot"
    description = "外部 API 集成演示"

    async def on_load(self):
        if not self.get_config("hitokoto_url"):
            self.set_config("hitokoto_url", DEFAULT_HITOKOTO_URL)
        self.data.setdefault("api_call_count", 0)
        LOG.info("ExternalAPI 已加载")

    # ---- 一言 API ----

    @registrar.on_group_command("每日一言")
    async def on_hitokoto(self, event: GroupMessageEvent):
        """调用一言 API"""
        url = self.get_config("hitokoto_url", DEFAULT_HITOKOTO_URL)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    params={"encode": "json"},
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status != 200:
                        await event.reply(f"⚠️ API 请求失败 (HTTP {resp.status})")
                        return

                    data = await resp.json()

            hitokoto = data.get("hitokoto", "获取失败")
            source = data.get("from", "未知")
            author = data.get("from_who", "")

            text = f"📜 {hitokoto}\n    —— {source}"
            if author:
                text += f" ({author})"

            self.data["api_call_count"] = self.data.get("api_call_count", 0) + 1
            await event.reply(text)

        except aiohttp.ClientError as e:
            LOG.error("一言 API 请求异常: %s", e)
            await event.reply("⚠️ 网络请求失败，请稍后重试")
        except Exception as e:
            LOG.error("一言 API 未知异常: %s", e)
            await event.reply("⚠️ 获取一言失败")

    # ---- 随机图片（使用本地 fallback） ----

    @registrar.on_group_command("随机图片")
    async def on_random_image(self, event: GroupMessageEvent):
        """发送示例图片"""
        if FALLBACK_IMAGE.exists():
            await self.api.post_group_msg(
                event.group_id,
                text="🖼️ 这是一张示例图片:",
                image=str(FALLBACK_IMAGE),
            )
        else:
            await event.reply("⚠️ 示例图片资源不存在")

    # ---- 配置管理 (CommandHook str 参数绑定) ----

    @registrar.on_group_command("设置一言源")
    async def on_set_api(self, event: GroupMessageEvent, new_url: str):
        """修改一言 API 地址 — new_url 由 CommandHook 自动提取"""
        # 基本校验
        if not new_url.startswith("http"):
            await event.reply("⚠️ URL 必须以 http:// 或 https:// 开头")
            return

        self.set_config("hitokoto_url", new_url)
        await event.reply(f"一言 API 已更新为: {new_url}")

    @registrar.on_group_command("api状态")
    async def on_api_status(self, event: GroupMessageEvent):
        """查看 API 配置和状态"""
        url = self.get_config("hitokoto_url", DEFAULT_HITOKOTO_URL)
        count = self.data.get("api_call_count", 0)

        await event.reply(f"🔌 API 状态:\n  一言 API: {url}\n  累计调用: {count} 次")
