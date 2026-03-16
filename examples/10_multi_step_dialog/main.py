"""
10_multi_step_dialog — 多步对话

演示功能:
  - wait_event 连续多次使用实现多步交互
  - Predicate 语法糖（from_event 自动推导同 session 条件）
  - 超时自动取消
  - 中途输入 "取消" 退出对话
  - @registrar.on_group_command() 触发对话

使用方式:
  群里发 "注册" → 依次输入名字→年龄→确认 → 保存
  群里发 "我的信息" → 查看已注册的信息
  对话中随时输入 "取消" 退出
"""

import asyncio

from ncatbot.core import from_event
from ncatbot.core import registrar
from ncatbot.event import GroupMessageEvent
from ncatbot.plugin import NcatBotPlugin
from ncatbot.utils import get_log

LOG = get_log("MultiStepDialog")

TIMEOUT = 30  # 每步超时秒数


class MultiStepDialogPlugin(NcatBotPlugin):
    name = "multi_step_dialog"
    version = "1.0.0"
    author = "NcatBot"
    description = "多步对话演示"

    async def on_load(self):
        self.data.setdefault("users", {})
        LOG.info("MultiStepDialog 插件已加载，已注册用户: %d", len(self.data["users"]))

    async def _wait_user_reply(self, event: GroupMessageEvent):
        """等待同 session（同用户同群）的下一条消息"""
        reply = await self.wait_event(
            predicate=from_event(event),
            timeout=TIMEOUT,
        )
        return reply.data.raw_message.strip()

    @registrar.on_group_command("注册")
    async def on_register(self, event: GroupMessageEvent):
        """多步注册流程"""
        gid = event.group_id
        uid = event.user_id

        # 步骤 1: 询问名字
        await event.reply(
            f"📝 开始注册！请输入你的名字（{TIMEOUT}秒内回复，输入「取消」退出）："
        )

        try:
            name = await self._wait_user_reply(event)
        except asyncio.TimeoutError:
            await self.api.post_group_msg(gid, text="⏰ 注册超时，已取消")
            return

        if name == "取消":
            await self.api.post_group_msg(gid, text="❌ 注册已取消")
            return

        # 步骤 2: 询问年龄
        await self.api.post_group_msg(gid, text=f"好的，{name}！请输入你的年龄：")

        try:
            age_str = await self._wait_user_reply(event)
        except asyncio.TimeoutError:
            await self.api.post_group_msg(gid, text="⏰ 注册超时，已取消")
            return

        if age_str == "取消":
            await self.api.post_group_msg(gid, text="❌ 注册已取消")
            return

        if not age_str.isdigit():
            await self.api.post_group_msg(gid, text="❌ 年龄必须是数字，注册已取消")
            return

        age = int(age_str)

        # 步骤 3: 确认
        await self.api.post_group_msg(
            gid,
            text=f"请确认你的信息:\n  名字: {name}\n  年龄: {age}\n回复「确认」完成注册：",
        )

        try:
            confirm = await self._wait_user_reply(event)
        except asyncio.TimeoutError:
            await self.api.post_group_msg(gid, text="⏰ 确认超时，已取消")
            return

        if confirm != "确认":
            await self.api.post_group_msg(gid, text="❌ 注册已取消")
            return

        # 保存数据
        self.data.setdefault("users", {})[str(uid)] = {
            "name": name,
            "age": age,
        }
        await self.api.post_group_msg(
            gid, text=f"✅ 注册成功！欢迎你，{name}（{age}岁）"
        )
        LOG.info("用户 %s 完成注册: %s, %d岁", uid, name, age)

    @registrar.on_group_command("我的信息")
    async def on_my_info(self, event: GroupMessageEvent):
        """查看已注册的信息"""
        uid = str(event.user_id)
        users = self.data.get("users", {})
        info = users.get(uid)

        if info:
            await event.reply(
                f"👤 你的注册信息:\n  名字: {info['name']}\n  年龄: {info['age']}"
            )
        else:
            await event.reply("你还没有注册，发送「注册」开始注册流程")
