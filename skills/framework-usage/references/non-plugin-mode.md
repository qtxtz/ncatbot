# 非插件模式参考

> 适合快速验证想法、简单 Bot、体验框架。无需 manifest.toml 或插件目录。

## 最小示例

```python
from ncatbot.app import BotClient
from ncatbot.core.registry import registrar
from ncatbot.event import GroupMessageEvent

bot = BotClient()

@registrar.on_group_command("hello", ignore_case=True)
async def on_hello(event: GroupMessageEvent):
    await event.reply(text="Hello, NcatBot!")

if __name__ == "__main__":
    bot.run()
```

## 与插件模式的区别

| | 非插件模式 | 插件模式 |
|---|---|---|
| 适合 | 快速原型、简单 Bot | 功能丰富、可维护 Bot |
| 代码组织 | 全在 `main.py` | 插件目录 + manifest.toml |
| handler | 普通函数（无 `self`） | 方法（有 `self`） |
| Mixin | 不支持 | 配置/数据/RBAC/定时任务 |
| 热重载 | 不支持 | 支持 |

## 命令参数自动绑定

CommandHook 根据类型注解自动提取参数（非插件/插件模式通用）：

```python
from ncatbot.types import At

# "echo 你好" → content="你好"
@registrar.on_group_command("echo")
async def on_echo(event: GroupMessageEvent, content: str):
    await event.reply(text=content)

# "禁言 @某人 60" → target=At对象, duration=60
@registrar.on_group_command("禁言")
async def on_ban(event: GroupMessageEvent, target: At = None, duration: int = 60):
    if target is None:
        await event.reply(text="请 @一个用户")
        return
    await event.reply(text=f"已禁言 {target.qq}，{duration} 秒")
```

**绑定规则**：

| 类型注解 | 绑定来源 |
|---------|---------|
| `At` | 消息中的下一个 @ 对象 |
| `int` / `float` | 文本 token 自动转换 |
| `str`（非最后参数） | 消费一个词 |
| `str`（最后参数） | 剩余全部文本 |
| 有默认值 | 缺失时使用默认值 |
| 必填且缺失 | 跳过 handler |

## 通知与请求事件

```python
from ncatbot.event import NoticeEvent, FriendRequestEvent
from ncatbot.types import MessageArray

@registrar.on_group_increase()
async def on_welcome(event):
    msg = MessageArray()
    msg.add_at(event.user_id)
    msg.add_text(" 欢迎加入！")
    await event.reply(rtf=msg)

@registrar.on_poke()
async def on_poke(event: NoticeEvent):
    if str(event.data.target_id) == str(event.self_id):
        await event.reply(text="别戳我！")

@registrar.on_friend_request()
async def on_friend(event: FriendRequestEvent):
    await event.approve()
```

## 多步对话

非插件模式通过 `bot.dispatcher.wait_event()` 实现：

```python
import asyncio

@registrar.on_group_command("注册")
async def on_register(event: GroupMessageEvent):
    await event.reply(text="请输入你的名字（30秒内）：")
    try:
        reply = await bot.dispatcher.wait_event(
            predicate=lambda e: (
                str(e.data.user_id) == str(event.user_id)
                and str(e.data.group_id) == str(event.group_id)
            ),
            timeout=30.0,
        )
        await event.reply(text=f"你好，{reply.data.raw_message.strip()}！")
    except asyncio.TimeoutError:
        await event.reply(text="超时，注册已取消")
```

> 插件模式用 `self.wait_event()` 代替 `bot.dispatcher.wait_event()`。

## 装饰器速查

所有装饰器在两种模式中完全相同（插件模式 handler 多 `self` 参数）。

| 装饰器 | 说明 |
|--------|------|
| `@registrar.on_command("cmd")` | 匹配命令（群+私聊） |
| `@registrar.on_group_command("cmd")` | 仅群命令 |
| `@registrar.on_private_command("cmd")` | 仅私聊命令 |
| `@registrar.on_group_message()` | 所有群消息 |
| `@registrar.on_private_message()` | 所有私聊消息 |
| `@registrar.on_message()` | 所有消息 |
| `@registrar.on_group_increase()` | 群成员增加 |
| `@registrar.on_group_decrease()` | 群成员减少 |
| `@registrar.on_poke()` | 戳一戳 |
| `@registrar.on_friend_request()` | 好友请求 |
| `@registrar.on_group_request()` | 群请求 |
| `@registrar.on("event.type")` | 通用注册 |

所有装饰器均支持 `priority`（越大越先执行）和 `ignore_case`（命令装饰器）。
