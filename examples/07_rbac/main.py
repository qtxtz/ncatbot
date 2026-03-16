"""
07_rbac — 权限管理系统

演示功能:
  - RBACMixin: add_permission / add_role / check_permission
  - self.rbac: assign_role / grant / revoke (底层 RBAC 服务)
  - @registrar.on_group_command() + At 参数绑定
  - 权限检查保护命令

使用方式:
  "授权 @xxx"     → 给用户授予 admin 角色
  "撤权 @xxx"     → 移除用户的 admin 角色
  "管理命令"       → 仅 admin 角色用户可执行
  "查权限"         → 查看自己是否有 admin 权限
  "权限信息"       → 查看当前 RBAC 系统配置
"""

from ncatbot.core import registrar
from ncatbot.event import GroupMessageEvent
from ncatbot.plugin import NcatBotPlugin
from ncatbot.types import At
from ncatbot.utils import get_log

LOG = get_log("RBAC")


class RBACPlugin(NcatBotPlugin):
    name = "rbac"
    version = "1.0.0"
    author = "NcatBot"
    description = "权限管理系统演示"

    async def on_load(self):
        # 注册权限路径
        self.add_permission("rbac.admin")
        self.add_permission("rbac.user")

        # 创建角色
        self.add_role("rbac_admin", exist_ok=True)
        self.add_role("rbac_user", exist_ok=True)

        # 给角色分配权限（通过底层 RBAC 服务）
        if self.rbac:
            self.rbac.grant("role", "rbac_admin", "rbac.admin")
            self.rbac.grant("role", "rbac_admin", "rbac.user")
            self.rbac.grant("role", "rbac_user", "rbac.user")

        LOG.info("RBAC 插件已加载，权限体系已初始化")

    # ---- 授权管理 ----

    @registrar.on_group_command("授权")
    async def on_grant(self, event: GroupMessageEvent, target: At = None):
        """授予用户 admin 角色 — At 参数由 CommandHook 自动绑定"""
        if target is None:
            await event.reply("请 @一个用户，例如: 授权 @xxx")
            return

        target_uid = str(target.qq)
        if self.rbac:
            self.rbac.assign_role("user", target_uid, "rbac_admin")
            await event.reply(f"已授予用户 {target_uid} 管理员权限 ✅")
        else:
            await event.reply("RBAC 服务不可用")

    @registrar.on_group_command("撤权")
    async def on_revoke(self, event: GroupMessageEvent, target: At = None):
        """移除用户 admin 角色"""
        if target is None:
            await event.reply("请 @一个用户，例如: 撤权 @xxx")
            return

        target_uid = str(target.qq)
        if self.rbac:
            self.rbac.unassign_role("user", target_uid, "rbac_admin")
            await event.reply(f"已移除用户 {target_uid} 的管理员权限 🚫")
        else:
            await event.reply("RBAC 服务不可用")

    # ---- 受权限保护的命令 ----

    @registrar.on_group_command("管理命令")
    async def on_admin_cmd(self, event: GroupMessageEvent):
        """仅 admin 角色可执行"""
        uid = str(event.user_id)
        if self.check_permission(uid, "rbac.admin"):
            await event.reply("🔑 管理命令执行成功！你拥有 admin 权限。")
        else:
            await event.reply("🚫 你没有执行此命令的权限（需要 rbac.admin）")

    # ---- 权限查询 ----

    @registrar.on_group_command("查权限")
    async def on_check_perm(self, event: GroupMessageEvent):
        """查看自己的权限"""
        uid = str(event.user_id)
        has_admin = self.check_permission(uid, "rbac.admin")
        has_user = self.check_permission(uid, "rbac.user")
        is_admin_role = self.user_has_role(uid, "rbac_admin")
        is_user_role = self.user_has_role(uid, "rbac_user")

        lines = [
            "👤 你的权限状态:",
            f"  角色 rbac_admin: {'✅' if is_admin_role else '❌'}",
            f"  角色 rbac_user: {'✅' if is_user_role else '❌'}",
            f"  权限 rbac.admin: {'✅' if has_admin else '❌'}",
            f"  权限 rbac.user: {'✅' if has_user else '❌'}",
        ]
        await event.reply("\n".join(lines))

    @registrar.on_group_command("权限信息")
    async def on_rbac_info(self, event: GroupMessageEvent):
        """查看 RBAC 系统配置信息"""
        await event.reply(
            "📋 RBAC 配置:\n"
            "  权限: rbac.admin, rbac.user\n"
            "  角色: rbac_admin (拥有 admin+user), rbac_user (拥有 user)\n"
            "  使用「授权 @xxx」分配管理员角色"
        )
