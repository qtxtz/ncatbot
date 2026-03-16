"""
11_group_manager — 群管理机器人

演示功能:
  - @registrar.on_group_command() + At/int 参数绑定: 踢人/禁言/改名片
  - RBAC 权限控制: 仅管理员可执行管理命令
  - @registrar.on_group_increase(): 新成员入群自动欢迎
  - ConfigMixin: 可配置欢迎语模板

综合场景: 一个完整可用的群管理工具

使用方式:
  "踢 @xxx"         → 踢出用户（需管理员权限）
  "禁言 @xxx 60"    → 禁言 60 秒
  "解禁 @xxx"       → 解除禁言
  "全体禁言"        → 开启全体禁言
  "解除全体禁言"    → 关闭全体禁言
  "改名片 @xxx 新名" → 修改群名片
  "设置欢迎语 xxx"   → 修改欢迎消息模板
  "授管理 @xxx"      → 授予管理权限
"""

from ncatbot.core import registrar
from ncatbot.event import GroupMessageEvent, GroupIncreaseEvent
from ncatbot.plugin import NcatBotPlugin
from ncatbot.types import At, MessageArray
from ncatbot.utils import get_log

LOG = get_log("GroupManager")
DEFAULT_WELCOME = "欢迎 {user} 加入本群！请先阅读群规 📜"


class GroupManagerPlugin(NcatBotPlugin):
    name = "group_manager"
    version = "1.0.0"
    author = "NcatBot"
    description = "群管理机器人"

    async def on_load(self):
        # 初始化 RBAC
        self.add_permission("group_manager.admin")
        self.add_role("gm_admin", exist_ok=True)
        if self.rbac:
            self.rbac.grant("role", "gm_admin", "group_manager.admin")

        # 默认配置
        if not self.get_config("welcome_template"):
            self.set_config("welcome_template", DEFAULT_WELCOME)

        LOG.info("GroupManager 已加载")

    def _is_admin(self, user_id) -> bool:
        return self.check_permission(str(user_id), "group_manager.admin")

    # ==================== 管理命令 (CommandHook 参数绑定) ====================

    @registrar.on_group_command("踢")
    async def on_kick(self, event: GroupMessageEvent, target: At = None):
        """踢出用户"""
        if not self._is_admin(event.user_id):
            await event.reply("🚫 你没有管理权限")
            return
        if target is None:
            await event.reply("请 @一个用户")
            return

        await self.api.manage.set_group_kick(event.group_id, target.qq)
        await event.reply(f"已踢出用户 {target.qq}")

    @registrar.on_group_command("禁言")
    async def on_ban(
        self, event: GroupMessageEvent, target: At = None, duration: int = 60
    ):
        """禁言用户 — At + int 参数由 CommandHook 自动绑定"""
        if not self._is_admin(event.user_id):
            await event.reply("🚫 你没有管理权限")
            return
        if target is None:
            await event.reply("请 @一个用户，例如: 禁言 @xxx 60")
            return

        await self.api.manage.set_group_ban(event.group_id, target.qq, duration)
        await event.reply(f"已禁言 {target.qq}，{duration} 秒")

    @registrar.on_group_command("解禁")
    async def on_unban(self, event: GroupMessageEvent, target: At = None):
        """解除禁言"""
        if not self._is_admin(event.user_id):
            await event.reply("🚫 你没有管理权限")
            return
        if target is None:
            await event.reply("请 @一个用户")
            return

        await self.api.manage.set_group_ban(event.group_id, target.qq, 0)
        await event.reply(f"已解除 {target.qq} 的禁言")

    @registrar.on_group_command("全体禁言")
    async def on_mute_all(self, event: GroupMessageEvent):
        """全体禁言"""
        if not self._is_admin(event.user_id):
            await event.reply("🚫 你没有管理权限")
            return
        await self.api.manage.set_group_whole_ban(event.group_id, True)
        await event.reply("已开启全体禁言 🔇")

    @registrar.on_group_command("解除全体禁言")
    async def on_unmute_all(self, event: GroupMessageEvent):
        """解除全体禁言"""
        if not self._is_admin(event.user_id):
            await event.reply("🚫 你没有管理权限")
            return
        await self.api.manage.set_group_whole_ban(event.group_id, False)
        await event.reply("已解除全体禁言 🔊")

    @registrar.on_group_command("改名片")
    async def on_set_card(
        self, event: GroupMessageEvent, target: At = None, new_card: str = ""
    ):
        """修改群名片 — At + str 参数自动绑定"""
        if not self._is_admin(event.user_id):
            await event.reply("🚫 你没有管理权限")
            return
        if target is None:
            await event.reply("请 @一个用户，例如: 改名片 @xxx 新名字")
            return

        await self.api.manage.set_group_card(event.group_id, target.qq, new_card)
        await event.reply(f"已将 {target.qq} 的群名片修改为: {new_card}")

    # ==================== 权限管理 ====================

    @registrar.on_group_command("授管理")
    async def on_grant_admin(self, event: GroupMessageEvent, target: At = None):
        """授予管理权限"""
        if target is None:
            return
        target_uid = str(target.qq)
        if self.rbac:
            self.rbac.assign_role("user", target_uid, "gm_admin")
            await event.reply(f"已授予 {target_uid} 群管理权限 ✅")

    # ==================== 欢迎消息 ====================

    @registrar.on_group_command("设置欢迎语")
    async def on_set_welcome(self, event: GroupMessageEvent, template: str):
        """设置欢迎语模板 — str 参数自动绑定"""
        self.set_config("welcome_template", template)
        await event.reply(f"欢迎语已更新为: {template}")

    @registrar.on_group_increase()
    async def on_member_join(self, event: GroupIncreaseEvent):
        """新成员入群自动欢迎 — 使用 registrar.on_group_increase()"""
        template = self.get_config("welcome_template", DEFAULT_WELCOME)
        welcome_text = template.replace("{user}", str(event.user_id))

        msg = MessageArray()
        msg.add_at(event.user_id)
        msg.add_text(f" {welcome_text}")

        await self.api.post_group_array_msg(event.group_id, msg)
