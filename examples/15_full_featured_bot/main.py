"""
15_full_featured_bot — 全功能群助手

演示功能 (综合覆盖所有框架特性):
  - 生命周期: on_load / on_close
  - @registrar.on_group_command() 命令匹配 + 参数绑定 (str/At/int)
  - @registrar.on_group_increase() 通知事件处理
  - MessageArray / At / Image 消息段
  - ConfigMixin / DataMixin / RBACMixin / TimeTaskMixin
  - 事件实体类型注解: GroupMessageEvent / GroupIncreaseEvent

使用方式:
  "帮助"            → 查看所有可用命令
  "签到"            → 每日签到获取积分
  "积分"            → 查看自己的积分
  "排行榜"          → 查看积分排行
  "设置前缀 !"       → 修改命令前缀
  "添加关键词 问题=答案" → 添加关键词自动回复
  "删除关键词 xxx"   → 删除关键词回复
  "关键词列表"       → 查看所有关键词
  "管理踢 @xxx"      → 管理员踢人
  "管理禁言 @xxx 60" → 管理员禁言
  "开启早安"         → 开启每日 7:30 自动早安消息
  "关闭早安"         → 关闭早安消息
  新成员入群         → 自动欢迎
"""

import random
import time

from ncatbot.core import registrar
from ncatbot.event import GroupMessageEvent, GroupIncreaseEvent
from ncatbot.plugin import NcatBotPlugin
from ncatbot.types import At, MessageArray
from ncatbot.utils import get_log

LOG = get_log("FullFeaturedBot")

HELP_TEXT = """🤖 全功能群助手 — 命令列表:

📋 基础功能:
  帮助         → 查看此帮助
  签到         → 每日签到获取积分
  积分         → 查看自己的积分
  排行榜       → 查看积分排行

⚙️ 配置管理:
  设置前缀 X   → 修改命令前缀
  查看配置     → 查看当前配置

💬 自动回复:
  添加关键词 Q=A → 添加关键词回复
  删除关键词 X   → 删除关键词
  关键词列表     → 查看所有关键词

🔧 管理命令 (需权限):
  管理踢 @xxx      → 踢出用户
  管理禁言 @xxx 60  → 禁言用户
  授权 @xxx         → 授予管理权限

⏰ 定时功能:
  开启早安     → 开启每日早安消息
  关闭早安     → 关闭早安消息"""


class FullFeaturedBotPlugin(NcatBotPlugin):
    name = "full_featured_bot"
    version = "1.0.0"
    author = "NcatBot"
    description = "全功能群助手"

    async def on_load(self):
        # ---- 配置初始化 ----
        if not self.get_config("prefix"):
            self.set_config("prefix", "")
        if not self.get_config("welcome_msg"):
            self.set_config("welcome_msg", "欢迎加入！发送「帮助」查看可用功能 📋")

        # ---- 数据初始化 ----
        self.data.setdefault("scores", {})
        self.data.setdefault("sign_in_dates", {})
        self.data.setdefault("keywords", {})
        self.data.setdefault("morning_groups", [])

        # ---- RBAC 初始化 ----
        self.add_permission("full_bot.admin")
        self.add_role("full_bot_admin", exist_ok=True)
        if self.rbac:
            self.rbac.grant("role", "full_bot_admin", "full_bot.admin")

        LOG.info("FullFeaturedBot 已加载")

    async def on_close(self):
        LOG.info("FullFeaturedBot 已关闭")

    def _is_admin(self, user_id) -> bool:
        return self.check_permission(str(user_id), "full_bot.admin")

    # ==================== 帮助 ====================

    @registrar.on_group_command("帮助")
    async def on_help(self, event: GroupMessageEvent):
        await event.reply(HELP_TEXT)

    # ==================== 签到与积分 ====================

    @registrar.on_group_command("签到")
    async def on_sign_in(self, event: GroupMessageEvent):
        """每日签到"""
        uid = str(event.user_id)
        today = time.strftime("%Y-%m-%d")
        sign_dates = self.data.setdefault("sign_in_dates", {})

        if sign_dates.get(uid) == today:
            await event.reply("你今天已经签到过了 ✅")
            return

        # 随机积分
        points = random.randint(1, 20)
        scores = self.data.setdefault("scores", {})
        scores[uid] = scores.get(uid, 0) + points
        sign_dates[uid] = today

        msg = MessageArray()
        msg.add_at(event.user_id)
        msg.add_text(f" 签到成功！获得 {points} 积分 🎉\n当前总积分: {scores[uid]}")

        await self.api.post_group_array_msg(event.group_id, msg)

    @registrar.on_group_command("积分")
    async def on_score(self, event: GroupMessageEvent):
        """查看积分"""
        uid = str(event.user_id)
        score = self.data.get("scores", {}).get(uid, 0)
        await event.reply(f"💰 你的积分: {score}")

    @registrar.on_group_command("排行榜")
    async def on_rank(self, event: GroupMessageEvent):
        """积分排行榜"""
        scores = self.data.get("scores", {})
        if not scores:
            await event.reply("还没有人签到过")
            return

        top = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:10]
        lines = ["🏆 积分排行榜:"]
        medals = ["🥇", "🥈", "🥉"]
        for i, (uid, score) in enumerate(top):
            medal = medals[i] if i < 3 else f" {i + 1}."
            lines.append(f"  {medal} {uid}: {score} 积分")

        await event.reply("\n".join(lines))

    # ==================== 关键词自动回复 ====================

    @registrar.on_group_command("添加关键词")
    async def on_add_keyword(self, event: GroupMessageEvent, content: str):
        """添加关键词回复: CommandHook 提取 "添加关键词" 后的文本"""
        if "=" not in content:
            await event.reply("格式: 添加关键词 问题=答案")
            return

        question, answer = content.split("=", 1)
        question, answer = question.strip(), answer.strip()
        if not question or not answer:
            await event.reply("问题和答案不能为空")
            return

        self.data.setdefault("keywords", {})[question] = answer
        await event.reply(f"✅ 关键词已添加: {question} → {answer}")

    @registrar.on_group_command("删除关键词")
    async def on_delete_keyword(self, event: GroupMessageEvent, keyword_name: str):
        """删除关键词 — keyword_name 由 CommandHook 自动提取"""
        keywords = self.data.get("keywords", {})
        if keyword_name in keywords:
            del keywords[keyword_name]
            await event.reply(f"✅ 已删除关键词: {keyword_name}")
        else:
            await event.reply(f"❌ 未找到关键词: {keyword_name}")

    @registrar.on_group_command("关键词列表")
    async def on_list_keywords(self, event: GroupMessageEvent):
        """查看关键词列表"""
        keywords = self.data.get("keywords", {})
        if not keywords:
            await event.reply("当前没有关键词回复")
            return

        lines = [f"💬 共 {len(keywords)} 个关键词:"]
        for q, a in keywords.items():
            lines.append(f"  {q} → {a}")

        await event.reply("\n".join(lines))

    @registrar.on_group_message(priority=30)
    async def on_keyword_match(self, event: GroupMessageEvent):
        """自动关键词匹配（使用 message.text）"""
        text = event.message.text.strip()
        keywords = self.data.get("keywords", {})

        for kw, reply_text in keywords.items():
            if kw in text:
                await event.reply(f"💬 {reply_text}")
                return

    # ==================== 配置管理 ====================

    @registrar.on_group_command("设置前缀")
    async def on_set_prefix(self, event: GroupMessageEvent, prefix: str):
        """设置命令前缀"""
        self.set_config("prefix", prefix)
        await event.reply(f"命令前缀已更新为: 「{prefix}」")

    @registrar.on_group_command("查看配置")
    async def on_view_config(self, event: GroupMessageEvent):
        """查看配置"""
        lines = ["⚙️ 当前配置:"]
        for k, v in self.config.items():
            lines.append(f"  {k}: {v}")
        await event.reply("\n".join(lines))

    # ==================== 管理命令 (RBAC + CommandHook 参数绑定) ====================

    @registrar.on_group_command("管理踢")
    async def on_admin_kick(self, event: GroupMessageEvent, target: At = None):
        """管理员踢人"""
        if not self._is_admin(event.user_id):
            await event.reply("🚫 你需要管理员权限")
            return
        if target is None:
            return

        await self.api.manage.set_group_kick(event.group_id, target.qq)
        await event.reply(f"已踢出 {target.qq}")

    @registrar.on_group_command("管理禁言")
    async def on_admin_ban(
        self, event: GroupMessageEvent, target: At = None, duration: int = 60
    ):
        """管理员禁言 — At + int 参数自动绑定"""
        if not self._is_admin(event.user_id):
            await event.reply("🚫 你需要管理员权限")
            return
        if target is None:
            return

        await self.api.manage.set_group_ban(event.group_id, target.qq, duration)
        await event.reply(f"已禁言 {target.qq}，{duration} 秒")

    @registrar.on_group_command("授权")
    async def on_grant(self, event: GroupMessageEvent, target: At = None):
        """授予管理权限"""
        if target is None:
            return
        uid = str(target.qq)
        if self.rbac:
            self.rbac.assign_role("user", uid, "full_bot_admin")
            await event.reply(f"✅ 已授予 {uid} 管理权限")

    # ==================== 定时早安 (TimeTask) ====================

    @registrar.on_group_command("开启早安")
    async def on_enable_morning(self, event: GroupMessageEvent):
        """开启早安"""
        gid = str(event.group_id)
        groups = self.data.setdefault("morning_groups", [])
        if gid not in groups:
            groups.append(gid)

        self.add_scheduled_task("morning_greeting", "07:30")
        await event.reply("☀️ 已开启每日 07:30 早安消息")

    @registrar.on_group_command("关闭早安")
    async def on_disable_morning(self, event: GroupMessageEvent):
        """关闭早安"""
        gid = str(event.group_id)
        groups = self.data.get("morning_groups", [])
        if gid in groups:
            groups.remove(gid)

        if not groups:
            self.remove_scheduled_task("morning_greeting")

        await event.reply("🌙 已关闭早安消息")

    async def morning_greeting(self):
        """定时早安回调"""
        greetings = [
            "☀️ 早安！新的一天开始了，加油！",
            "🌅 早上好！今天也要元气满满哦~",
            "🌞 早安！美好的一天从现在开始！",
            "🌄 起床啦！祝你今天一切顺利～",
        ]
        msg = random.choice(greetings)

        for gid in self.data.get("morning_groups", []):
            try:
                await self.api.post_group_msg(gid, text=msg)
            except Exception as e:
                LOG.error("发送早安到群 %s 失败: %s", gid, e)

    # ==================== 欢迎新成员 (Notice) ====================

    @registrar.on_group_increase()
    async def on_new_member(self, event: GroupIncreaseEvent):
        """新成员入群欢迎 — 使用 registrar.on_group_increase()"""
        welcome = self.get_config("welcome_msg", "欢迎加入！")

        msg = MessageArray()
        msg.add_at(event.user_id)
        msg.add_text(f" {welcome}")

        await self.api.post_group_array_msg(event.group_id, msg)
