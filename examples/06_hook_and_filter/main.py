"""
06_hook_and_filter — Hook 系统与过滤器

演示功能:
  - 自定义 BEFORE_CALL Hook: 关键词屏蔽（使用 message.text 而非 raw_message）
  - 自定义 AFTER_CALL Hook: 命令执行日志记录
  - 自定义 ON_ERROR Hook: 异常自动通知（使用 ctx.api）
  - @registrar.on_group_command() 命令装饰器 + 参数绑定
  - add_hooks 批量绑定 Hook

使用方式:
  群里发 "回声 你好"    → 回复 "你好"（经过关键词过滤）
  群里发 "回声 违禁词"  → 被 Hook 拦截，不回复
  群里发 "除零"         → 触发异常，ON_ERROR Hook 自动回复错误信息
  私聊发 "私聊测试"     → private_only 过滤器允许通过
"""

from ncatbot.core import registrar, Hook, HookAction, HookContext, HookStage, add_hooks
from ncatbot.event import GroupMessageEvent, PrivateMessageEvent
from ncatbot.plugin import NcatBotPlugin
from ncatbot.types import MessageArray
from ncatbot.utils import get_log

LOG = get_log("HookAndFilter")

# 屏蔽词列表
BLOCKED_WORDS = ["违禁词", "广告", "spam"]


# ==================== 自定义 Hook ====================


class KeywordFilterHook(Hook):
    """BEFORE_CALL: 检查 message.text（结构化文本）是否包含屏蔽词"""

    stage = HookStage.BEFORE_CALL
    priority = 50

    async def execute(self, ctx: HookContext) -> HookAction:
        message = getattr(ctx.event.data, "message", None)
        if message is None:
            return HookAction.CONTINUE
        text = message.text if hasattr(message, "text") else ""
        for word in BLOCKED_WORDS:
            if word in text:
                LOG.info("消息被屏蔽词过滤: %s", text)
                return HookAction.SKIP
        return HookAction.CONTINUE


class LoggingHook(Hook):
    """AFTER_CALL: 记录命令成功执行的日志"""

    stage = HookStage.AFTER_CALL
    priority = 0

    async def execute(self, ctx: HookContext) -> HookAction:
        handler_name = ctx.handler_entry.func.__name__
        user_id = getattr(ctx.event.data, "user_id", "unknown")
        LOG.info("[日志 Hook] %s 被 %s 成功执行", handler_name, user_id)
        return HookAction.CONTINUE


class ErrorNotifyHook(Hook):
    """ON_ERROR: 异常时通过 ctx.api 自动回复错误信息"""

    stage = HookStage.ON_ERROR
    priority = 0

    async def execute(self, ctx: HookContext) -> HookAction:
        error = ctx.error
        LOG.error("[错误 Hook] handler 异常: %s", error)
        # 使用 HookContext.api (必填字段) 回复用户
        api = ctx.api
        data = ctx.event.data
        if api and hasattr(data, "group_id"):
            try:
                msg = MessageArray()
                msg.add_text(f"⚠️ 命令执行出错: {type(error).__name__}")
                await api.post_group_array_msg(data.group_id, msg)
            except Exception:
                pass
        return HookAction.CONTINUE


# 预实例化 Hook
keyword_filter = KeywordFilterHook()
logging_hook = LoggingHook()
error_notify = ErrorNotifyHook()


class HookAndFilterPlugin(NcatBotPlugin):
    name = "hook_and_filter"
    version = "1.0.0"
    author = "NcatBot"
    description = "Hook 系统与过滤器演示"

    async def on_load(self):
        LOG.info("HookAndFilter 插件已加载")

    # ---- 使用 add_hooks 批量绑定 + CommandHook 参数绑定 ----

    @add_hooks(keyword_filter, logging_hook, error_notify)
    @registrar.on_group_command("回声")
    async def on_echo(self, event: GroupMessageEvent, content: str):
        """回声命令（经过关键词过滤 + 日志记录 + 错误捕获）
        CommandHook 自动提取 "回声" 后面的文本作为 content 参数"""
        await event.reply(f"🔊 {content}")

    # ---- 使用 Hook 装饰器语法 ----

    @error_notify
    @registrar.on_group_command("除零")
    async def on_divide_by_zero(self, event: GroupMessageEvent):
        """故意触发异常，演示 ON_ERROR Hook"""
        _ = 1 / 0  # 触发 ZeroDivisionError

    # ---- 使用 on_private_command / on_group_command 替代手动 raw_message 检查 ----

    @registrar.on_private_command("私聊测试")
    async def on_private_test(self, event: PrivateMessageEvent):
        """仅私聊消息触发"""
        await event.reply("✅ 这是私聊专属回复（MessageTypeFilter 过滤了群消息）")

    @registrar.on_group_command("群聊测试")
    async def on_group_test(self, event: GroupMessageEvent):
        """仅群聊消息触发"""
        await event.reply("✅ 这是群聊专属回复")
