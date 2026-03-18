# 单元测试

按 NcatBot 模块组织的单元测试，每个子目录对应一个源码模块。

## 模块映射

| 目录 | 源码模块 | 规范范围 |
|------|----------|----------|
| [types/](types/) | `ncatbot.types` | T-01 ~ T-14, S-01 ~ S-10, CQ-01 ~ CQ-08, N-01 ~ N-05 |
| [event/](event/) | `ncatbot.event` | E-01 ~ E-07 |
| [api/](api/) | `ncatbot.api` | A-01 ~ A-04, AE-01 ~ AE-07 |
| [core/](core/) | `ncatbot.core` | D-01 ~ D-09, K-01 ~ K-22, H-01 ~ H-12, R-01 ~ R-09 |
| [service/](service/) | `ncatbot.service` | SM-01 ~ SM-08 |
| [plugin/](plugin/) | `ncatbot.plugin.mixin` | M-01 ~ M-41, ID-01 ~ ID-02 |
| [adapter/](adapter/) | `ncatbot.adapter.napcat` | P-01 ~ P-07, RF-01 ~ RF-08, AR-01 ~ AR-05, GM-01 ~ GM-05, BL-01 ~ BL-14, GH-01 ~ GH-11 |
| [config/](config/) | `ncatbot.utils.config` | CF-01 ~ CF-06 |

## 公共 Fixtures (`conftest.py`)

| Fixture | 类型 | 说明 |
|---------|------|------|
| `mock_api` | sync | `MockBotAPI` 实例 |
| `event_dispatcher` | async | `AsyncEventDispatcher`，测试后自动 `close()` |
| `handler_dispatcher` | async | `HandlerDispatcher`，测试后自动 `stop()` |
| `fresh_registrar` | sync | 全新 `Registrar`，自动清理全局 `_pending_handlers` |
| `tmp_plugin_workspace` | sync | 临时插件工作目录 (`tmp_path` 子目录) |
