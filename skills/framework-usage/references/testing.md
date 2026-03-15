# 插件测试参考

> 参考文档：[guide/testing/](docs/guide/testing/), [reference/testing/](docs/reference/testing/)

## 测试模板

```python
import pytest
from pathlib import Path
from ncatbot.testing import PluginTestHarness, group_message, private_message

pytestmark = pytest.mark.asyncio

PLUGIN_NAME = "my_plugin"

@pytest.fixture
def plugin_dir():
    return Path(__file__).resolve().parents[3] / "examples"

async def test_plugin_loads(plugin_dir):
    async with PluginTestHarness(
        plugin_names=[PLUGIN_NAME], plugin_dir=plugin_dir
    ) as h:
        assert PLUGIN_NAME in h.loaded_plugins

async def test_command(plugin_dir):
    async with PluginTestHarness(
        plugin_names=[PLUGIN_NAME], plugin_dir=plugin_dir
    ) as h:
        await h.inject(group_message("hello", group_id="100", user_id="99"))
        await h.settle(0.1)
        assert h.api_called("send_group_msg")
```

## 事件工厂函数

| 函数 | 说明 |
|------|------|
| `group_message(text, group_id=, user_id=)` | 群消息 |
| `private_message(text, user_id=)` | 私聊消息 |
| `friend_request()` | 好友请求 |
| `group_request()` | 群请求 |
| `group_increase()` | 群成员增加 |
| `group_decrease()` | 群成员减少 |
| `group_ban()` | 群禁言 |
| `poke()` | 戳一戳 |

## Scenario 构建器

```python
from ncatbot.testing import Scenario, group_message

await (
    Scenario("签到流程")
    .inject(group_message("签到", group_id="100", user_id="99"))
    .settle()
    .assert_api_called("send_group_msg")
    .run(harness)
)
```

## settle 时间建议

| 场景 | settle |
|------|--------|
| 简单 handler | `0.05` |
| 复杂 handler | `0.2` |
| 含 `wait_event` 的多步对话 | `0.5` |

## Mock API 响应

```python
h.mock_api.set_response("get_group_member_info", {"user_id": "99", "nickname": "test"})
```

未配置的 API 返回空 `{}`。

## 多步对话测试

每步之间用 `h.reset_api()` 清除调用记录：

```python
async def test_dialog(plugin_dir):
    async with PluginTestHarness(
        plugin_names=[PLUGIN_NAME], plugin_dir=plugin_dir
    ) as h:
        await h.inject(group_message("注册", group_id="100", user_id="99"))
        await h.settle(0.1)
        assert h.api_called("send_group_msg")

        h.reset_api()
        await h.inject(group_message("张三", group_id="100", user_id="99"))
        await h.settle(0.1)
        assert h.api_called("send_group_msg")
```

## 调试工具

```python
# 打印所有 API 调用
for call in h.api_calls:
    print(f"  {call.action}({call.args}, {call.kwargs})")

# 已加载插件
print(h.loaded_plugins)

# 获取插件实例
plugin = h.get_plugin("my_plugin")
print(plugin.data, plugin.config)
```

## 常见失败原因

| 症状 | 原因 | 修复 |
|------|------|------|
| "插件 xxx 未索引" | `plugin_dir` 路径错误 | 应指向父目录，非插件文件夹本身 |
| `api_called()` 失败 | 命令文本不匹配 | 确认注入文本与命令一致 |
| `api_called()` 失败 | settle 不足 | 增大到 `settle(0.2)` |
| `api_called()` 失败 | Hook 拦截 | 检查 `@add_hooks` 装饰器 |
| `api_called()` 失败 | 事件类型不匹配 | 群用 `group_message()`，私聊用 `private_message()` |
| RBAC 不可用 | `skip_builtin=True` | 默认不加载内置服务，RBACMixin 做降级处理 |
| 依赖插件缺失 | 不在同一 `plugin_dir` | 确保所有依赖在同目录下 |
