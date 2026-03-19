"""
common/08_command_group — 命令组分层路由插件

演示功能:
  - CommandGroupHook 与 CommandHook 一致的使用方式
  - 参数类型自动绑定（int/float/str/At）
  - 命令别名和子命令别名
  - ignore_case 匹配
  - @hook.subcommand() 装饰器注册
"""

from ncatbot.core import CommandGroupHook, group_only, registrar
from ncatbot.event.qq import GroupMessageEvent
from ncatbot.plugin import NcatBotPlugin


class CommandGroupDemoPlugin(NcatBotPlugin):
    name = "command_group_common"
    version = "1.0.0"
    author = "NcatBot"
    description = "命令组分层路由示例 — CommandGroup + CommandGroupHook"

    # ============================================================================
    # 方案 1: 简单子命令
    # ============================================================================
    admin_hook = CommandGroupHook("admin", "/admin", "a", ignore_case=True)

    @admin_hook.subcommand("kick", "remove")
    async def admin_kick(self, event: GroupMessageEvent, user_id: int):
        """移除成员: /admin kick 12345"""
        await event.api.manage.set_group_kick(group_id=event.group_id, user_id=user_id)

    @admin_hook.subcommand("ban")
    async def admin_ban(
        self, event: GroupMessageEvent, user_id: int, minutes: int = 60
    ):
        """禁言成员: /admin ban 12345 120"""
        await event.api.manage.set_group_ban(
            group_id=event.group_id,
            user_id=user_id,
            duration=minutes * 60,
        )

    @registrar.on_group_message()
    @group_only
    @admin_hook
    async def on_admin(self, event: GroupMessageEvent):
        """处理 admin 命令组"""
        pass

    # ============================================================================
    # 方案 2: 参数绑定示例
    # ============================================================================
    calc_hook = CommandGroupHook("calc")

    @calc_hook.subcommand("add")
    async def calc_add(self, event: GroupMessageEvent, a: int, b: int):
        result = a + b
        await event.reply(f"{a} + {b} = {result}")

    @calc_hook.subcommand("divide")
    async def calc_divide(self, event: GroupMessageEvent, a: float, b: float):
        if b == 0:
            await event.reply("Error: Division by zero")
        else:
            result = a / b
            await event.reply(f"{a} / {b} = {result}")

    @calc_hook.subcommand("echo")
    async def calc_echo(self, event: GroupMessageEvent, text: str):
        """回显文本：最后一个 str 参数获取剩余全部内容"""
        await event.reply(text)

    @registrar.on_group_message()
    @group_only
    @calc_hook
    async def on_calc(self, event: GroupMessageEvent):
        """处理计算器命令"""
        pass

    # ============================================================================
    # 方案 3: 多命令别名
    # ============================================================================
    help_hook = CommandGroupHook("help", "?", ignore_case=True)

    @help_hook.subcommand("admin")
    async def help_admin(self, event: GroupMessageEvent):
        await event.reply(
            "Admin Commands:\n/admin kick <id>\n/admin ban <id> [minutes]"
        )

    @help_hook.subcommand("calc")
    async def help_calc(self, event: GroupMessageEvent):
        await event.reply(
            "Calc Commands:\n/calc add <a> <b>\n/calc divide <a> <b>\n/calc echo <text>"
        )

    @registrar.on_group_message()
    @group_only
    @help_hook
    async def on_help(self, event: GroupMessageEvent):
        """处理帮助命令 (支持 /help 或 /?)"""
        pass
