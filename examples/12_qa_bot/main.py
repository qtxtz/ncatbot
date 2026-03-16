"""
12_qa_bot — 问答机器人

演示功能:
  - DataMixin 数据持久化: 问答对存储在 self.data
  - wait_event 多步对话: 添加问答时依次输入问题和答案
  - @registrar.on_group_command() 命令装饰器 + str 参数绑定
  - 关键词精确匹配与模糊匹配

使用方式:
  "添加问答"        → 进入多步对话，依次输入问题和答案
  "删除问答 xxx"    → 删除指定问题
  "问答列表"        → 列出所有问答对
  直接发送匹配的问题 → 自动回复对应答案
"""

import asyncio

from ncatbot.core import registrar
from ncatbot.event import GroupMessageEvent
from ncatbot.plugin import NcatBotPlugin
from ncatbot.utils import get_log

LOG = get_log("QABot")

TIMEOUT = 30


class QABotPlugin(NcatBotPlugin):
    name = "qa_bot"
    version = "1.0.0"
    author = "NcatBot"
    description = "问答机器人"

    async def on_load(self):
        self.data.setdefault("qa_pairs", {})
        LOG.info("QABot 已加载，当前 %d 个问答对", len(self.data["qa_pairs"]))

    async def _wait_reply(self, group_id, user_id):
        event = await self.wait_event(
            predicate=lambda e: (
                hasattr(e.data, "user_id")
                and str(e.data.user_id) == str(user_id)
                and hasattr(e.data, "group_id")
                and str(e.data.group_id) == str(group_id)
                and hasattr(e.data, "raw_message")
            ),
            timeout=TIMEOUT,
        )
        return event.data.raw_message.strip()

    # ---- 添加问答（多步对话） ----

    @registrar.on_group_command("添加问答")
    async def on_add_qa(self, event: GroupMessageEvent):
        """多步对话添加问答对"""
        gid, uid = event.group_id, event.user_id

        await event.reply("📝 请输入问题（输入「取消」退出）：")
        try:
            question = await self._wait_reply(gid, uid)
        except asyncio.TimeoutError:
            await self.api.post_group_msg(gid, text="⏰ 超时，已取消")
            return

        if question == "取消":
            await self.api.post_group_msg(gid, text="❌ 已取消")
            return

        await self.api.post_group_msg(
            gid, text=f"好的，问题是「{question}」\n请输入答案："
        )
        try:
            answer = await self._wait_reply(gid, uid)
        except asyncio.TimeoutError:
            await self.api.post_group_msg(gid, text="⏰ 超时，已取消")
            return

        if answer == "取消":
            await self.api.post_group_msg(gid, text="❌ 已取消")
            return

        self.data.setdefault("qa_pairs", {})[question] = answer
        await self.api.post_group_msg(
            gid, text=f"✅ 问答已添加:\n  Q: {question}\n  A: {answer}"
        )
        LOG.info("添加问答: %s -> %s", question, answer)

    # ---- 删除问答 (CommandHook str 参数绑定) ----

    @registrar.on_group_command("删除问答")
    async def on_delete_qa(self, event: GroupMessageEvent, question: str):
        """删除指定问答 — question 由 CommandHook 自动提取"""
        qa_pairs = self.data.get("qa_pairs", {})

        if question in qa_pairs:
            del qa_pairs[question]
            await event.reply(f"✅ 已删除问答: {question}")
        else:
            await event.reply(f"❌ 未找到问题: {question}")

    # ---- 问答列表 ----

    @registrar.on_group_command("问答列表")
    async def on_list_qa(self, event: GroupMessageEvent):
        """列出所有问答对"""
        qa_pairs = self.data.get("qa_pairs", {})
        if not qa_pairs:
            await event.reply("📋 当前没有问答对，发送「添加问答」来创建")
            return

        lines = [f"📋 共 {len(qa_pairs)} 个问答对:"]
        for i, (q, a) in enumerate(qa_pairs.items(), 1):
            lines.append(f"  {i}. Q: {q}")
            lines.append(f"     A: {a}")

        await event.reply("\n".join(lines))

    # ---- 自动匹配回复 ----

    @registrar.on_group_message(priority=50)
    async def on_auto_reply(self, event: GroupMessageEvent):
        """自动匹配问答并回复（使用 message.text 而非 raw_message）"""
        text = event.message.text.strip()
        # 跳过命令
        if text in ("添加问答", "问答列表") or text.startswith("删除问答"):
            return

        qa_pairs = self.data.get("qa_pairs", {})

        # 精确匹配
        if text in qa_pairs:
            await event.reply(f"💬 {qa_pairs[text]}")
            return

        # 模糊匹配
        for question, answer in qa_pairs.items():
            if question in text:
                await event.reply(f"💬 {answer}")
                return
