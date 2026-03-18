# 多平台使用参考

> 参考文档：[guide/multi_platform/](docs/guide/multi_platform/), [guide/adapter/](docs/guide/adapter/)（各平台登录与配置）, [reference/adapter/](docs/reference/adapter/), [reference/api/](docs/reference/api/)

## 各平台登录与配置

| 平台 | 认证方式 | 指南 |
|------|---------|------|
| QQ (NapCat) | WebUI 扫码 / 快速登录 | `docs/guide/adapter/1_napcat_qq.md` |
| Bilibili | 终端扫码 (bilibili-api-python) | `docs/guide/adapter/2_bilibili.md` |
| GitHub | Personal Access Token | `docs/guide/adapter/3_github.md` |
| Mock | 无需认证 | `docs/guide/adapter/4_mock.md` |

## 多适配器启动

```python
from ncatbot.app import BotClient
from ncatbot.adapter import NapCatAdapter
from ncatbot.adapter.github import GitHubAdapter

bot = BotClient(adapters=[
    NapCatAdapter(),           # platform="qq"
    GitHubAdapter(),           # platform="github"
    # TelegramAdapter(),       # platform="telegram" (未来)
])
bot.run()
```

每个适配器的 `platform` 必须唯一，重复会抛 `ValueError`。

### GitHub 适配器配置

GitHub 适配器支持 Webhook 和 Polling 两种模式：

```yaml
# config.yaml
adapters:
  - type: github
    token: "ghp_xxxx"          # GitHub Personal Access Token
    repos:
      - "owner/repo1"
      - "owner/repo2"
    mode: webhook              # "webhook"(default) | "polling"
    # Webhook 模式
    webhook_host: "0.0.0.0"
    webhook_port: 8080
    webhook_path: "/webhook"
    webhook_secret: "your-secret"
    # Polling 模式
    poll_interval: 60.0
```

## 多平台 API 访问

```python
# 默认委托（第一个注册的平台）
await api.send_group_msg(group_id, message)

# 显式平台
await api.qq.send_group_msg(group_id, message)
await api.github.create_issue_comment(repo, issue_number, body)
# await api.platform("telegram").send_message(chat_id, text)

# 查看已注册平台
print(api.platforms)  # {"qq": <QQAPIClient>, "github": <GitHubBotAPI>, ...}
```

## 平台过滤

所有装饰器均支持 `platform` 参数：

```python
@registrar.on_group_message(platform="qq")
async def qq_only(event): ...

@registrar.on_command("/help", platform="qq")
async def help_cmd(event): ...

@registrar.on_message()  # 不指定 = 所有平台
async def all_platforms(event):
    print(event.platform)
```

## Trait 协议（跨平台编程）

### API Trait（`ncatbot.api.traits`）

| Trait | 方法 |
|---|---|
| `IMessaging` | `send_private_msg`, `send_group_msg`, `delete_msg`, `send_forward_msg` |
| `IGroupManage` | `set_group_kick`, `set_group_ban`, `set_group_admin`, ... |
| `IQuery` | `get_login_info`, `get_friend_list`, `get_group_list`, ... |
| `IFileTransfer` | `upload_group_file`, `download_file` |

### Event Trait（`ncatbot.event.common.mixins`，通过 `ncatbot.event` 重新导出）

| Trait | 能力 |
|---|---|
| `Replyable` | `reply()`, `send()` |
| `Deletable` | `delete()` |
| `HasSender` | `sender` 属性 |
| `GroupScoped` | `group_id` 属性 |
| `Kickable` | `kick()` |
| `Bannable` | `ban()` |

### 跨平台 handler 示例

```python
from ncatbot.event import Replyable, GroupScoped

@bot.on("message")
async def handler(event):
    if isinstance(event, Replyable):
        await event.reply("收到!")
    if isinstance(event, GroupScoped):
        print(f"群 {event.group_id}")
```

## event.platform

所有事件实体都有 `platform` 属性（字符串），来自适配器的 `platform` 类属性。

```python
@bot.on("message")
async def handler(event):
    if event.platform == "qq":
        # QQ 专用逻辑
        ...
```
