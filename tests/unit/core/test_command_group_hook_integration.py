"""
命令组 Hook 集成测试 — 验证参数绑定和匹配流程
"""

import pytest
from unittest.mock import MagicMock

from ncatbot.core import CommandGroup, CommandGroupHook
from ncatbot.core.registry.hook import HookContext, HookAction
from ncatbot.event.qq import GroupMessageEvent


@pytest.mark.asyncio
async def test_full_workflow_command_matching():
    """测试完整的命令组匹配流程"""
    # 1. 创建命令组并注册子命令
    admin_group = CommandGroup(["admin", "a"])

    @admin_group.command("kick", "remove")
    async def admin_kick(event: GroupMessageEvent, user_id: int):
        pass

    @admin_group.command("ban")
    async def admin_ban(event: GroupMessageEvent, user_id: int, minutes: int = 60):
        pass

    # 2. 创建 hook
    admin_hook = CommandGroupHook(admin_group, ignore_case=True)

    # 3. 模拟事件
    event = MagicMock(spec=GroupMessageEvent)
    event.data = MagicMock()
    event.data.message = MagicMock()
    event.data.message.filter_at = MagicMock(return_value=[])

    handler_entry = MagicMock()
    handler_entry.func = lambda e, user_id: None

    api = MagicMock()

    # 4. 测试 kick 命令匹配
    event.data.message.text = "admin kick 12345"

    ctx = HookContext(
        event=event,
        event_type="message.group",
        handler_entry=handler_entry,
        api=api,
    )

    result = await admin_hook.execute(ctx)
    # 匹配成功且参数绑定正确
    assert result == HookAction.CONTINUE
    assert "user_id" in ctx.kwargs
    assert ctx.kwargs["user_id"] == 12345

    # 5. 测试 ban 命令匹配 (大小写忽略)
    event.data.message.text = "ADMIN ban 54321 120"
    ctx.kwargs = {}

    ctx = HookContext(
        event=event,
        event_type="message.group",
        handler_entry=handler_entry,
        api=api,
    )

    result = await admin_hook.execute(ctx)
    assert result == HookAction.CONTINUE
    assert ctx.kwargs["user_id"] == 54321
    assert ctx.kwargs["minutes"] == 120

    # 6. 测试默认参数
    event.data.message.text = "admin ban 99999"
    ctx.kwargs = {}

    ctx = HookContext(
        event=event,
        event_type="message.group",
        handler_entry=handler_entry,
        api=api,
    )

    result = await admin_hook.execute(ctx)
    assert result == HookAction.CONTINUE
    assert ctx.kwargs["user_id"] == 99999
    assert ctx.kwargs["minutes"] == 60  # 默认值


@pytest.mark.asyncio
async def test_multiple_command_groups_routing():
    """测试多个命令组的路由"""
    # 创建多个命令组
    help_group = CommandGroup(["help", "h"])
    admin_group = CommandGroup(["admin", "a"])

    @help_group.command("all")
    async def help_all(event: GroupMessageEvent):
        pass

    @admin_group.command("ban")
    async def admin_ban(event: GroupMessageEvent, user_id: int):
        pass

    # 创建并列 hook
    multi_hook = CommandGroupHook(help_group, admin_group, ignore_case=True)

    # 创建事件和处理器
    event = MagicMock(spec=GroupMessageEvent)
    event.data = MagicMock()
    event.data.message = MagicMock()
    event.data.message.filter_at = MagicMock(return_value=[])

    handler_entry = MagicMock()
    handler_entry.func = lambda e: None

    api = MagicMock()

    # 测试 help 命令路由 (第一个命令组)
    event.data.message.text = "HELP all"

    ctx = HookContext(
        event=event,
        event_type="message.group",
        handler_entry=handler_entry,
        api=api,
    )

    result = await multi_hook.execute(ctx)
    assert result == HookAction.CONTINUE

    # 测试 admin 命令路由 (第二个命令组)
    event.data.message.text = "admin ban 12345"
    ctx.kwargs = {}

    ctx = HookContext(
        event=event,
        event_type="message.group",
        handler_entry=handler_entry,
        api=api,
    )

    result = await multi_hook.execute(ctx)
    assert result == HookAction.CONTINUE
    assert ctx.kwargs["user_id"] == 12345


@pytest.mark.asyncio
async def test_parameter_binding_all_types():
    """测试所有类型参数绑定"""
    group = CommandGroup(["test"])

    @group.command("all")
    async def test_all(event: GroupMessageEvent, name: str, count: int, ratio: float):
        pass

    hook = CommandGroupHook(group)

    # 创建事件
    event = MagicMock(spec=GroupMessageEvent)
    event.data = MagicMock()
    event.data.message = MagicMock()
    event.data.message.text = "test all alice 42 3.14"
    event.data.message.filter_at = MagicMock(return_value=[])

    handler_entry = MagicMock()
    handler_entry.func = lambda e: None

    api = MagicMock()

    ctx = HookContext(
        event=event,
        event_type="message.group",
        handler_entry=handler_entry,
        api=api,
    )

    result = await hook.execute(ctx)

    assert result == HookAction.CONTINUE
    # 验证参数绑定
    assert ctx.kwargs["name"] == "alice"
    assert ctx.kwargs["count"] == 42
    assert ctx.kwargs["ratio"] == 3.14


@pytest.mark.asyncio
async def test_optional_parameters():
    """测试可选参数绑定"""
    group = CommandGroup(["calc"])

    @group.command("sum")
    async def calc_sum(event: GroupMessageEvent, a: int, b: int = 10):
        pass

    hook = CommandGroupHook(group)

    event = MagicMock(spec=GroupMessageEvent)
    event.data = MagicMock()
    event.data.message = MagicMock()
    event.data.message.filter_at = MagicMock(return_value=[])

    handler_entry = MagicMock()
    handler_entry.func = lambda e: None

    api = MagicMock()

    # 测试只提供必选参数 (使用默认值)
    event.data.message.text = "calc sum 5"

    ctx = HookContext(
        event=event,
        event_type="message.group",
        handler_entry=handler_entry,
        api=api,
    )

    result = await hook.execute(ctx)
    assert result == HookAction.CONTINUE
    assert ctx.kwargs["a"] == 5
    assert ctx.kwargs["b"] == 10

    # 测试提供所有参数 (覆盖默认值)
    event.data.message.text = "calc sum 5 20"
    ctx.kwargs = {}

    ctx = HookContext(
        event=event,
        event_type="message.group",
        handler_entry=handler_entry,
        api=api,
    )

    result = await hook.execute(ctx)
    assert result == HookAction.CONTINUE
    assert ctx.kwargs["a"] == 5
    assert ctx.kwargs["b"] == 20


def test_command_group_alias():
    """测试命令别名"""
    group = CommandGroup(["help", "h", "?"])
    assert group.names == ["help", "h", "?"]

    @group.command("admin", "a", "adm")
    async def help_admin(event):
        pass

    # 所有别名都应该注册
    assert "admin" in group.subcommands
    assert "a" in group.subcommands
    assert "adm" in group.subcommands


def test_command_group_hook_string_repr():
    """测试 CommandGroupHook 的字符串表示"""
    group1 = CommandGroup(["help"])
    group2 = CommandGroup(["admin"])

    hook = CommandGroupHook(group1, group2, ignore_case=True, priority=100)

    repr_str = repr(hook)
    assert "CommandGroupHook" in repr_str
    assert "ignore_case=True" in repr_str


@pytest.mark.asyncio
async def test_string_parameter_with_spaces():
    """测试最后一个 str 参数获取剩余全部文本"""
    group = CommandGroup(["echo"])

    @group.command("msg")
    async def echo_msg(event: GroupMessageEvent, message: str):
        pass

    hook = CommandGroupHook(group)

    event = MagicMock(spec=GroupMessageEvent)
    event.data = MagicMock()
    event.data.message = MagicMock()
    event.data.message.text = "echo msg hello world this is a test"
    event.data.message.filter_at = MagicMock(return_value=[])

    handler_entry = MagicMock()
    handler_entry.func = lambda e: None

    api = MagicMock()

    ctx = HookContext(
        event=event,
        event_type="message.group",
        handler_entry=handler_entry,
        api=api,
    )

    result = await hook.execute(ctx)
    assert result == HookAction.CONTINUE
    # 最后一个 str 参数应该获取剩余全部文本
    assert ctx.kwargs["message"] == "hello world this is a test"
