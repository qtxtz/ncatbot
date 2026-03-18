# API 模块测试

源码模块: `ncatbot.api`

## 验证规范

### BotAPIClient (`test_api_client.py`)

| 规范 ID | 说明 | 验证点 |
|---------|------|--------|
| A-01 | 高频方法平铺 | `send_group_msg` 等可直接调用 |
| A-02 | `manage` 命名空间 | 包含 `set_group_kick` 等群管操作 |
| A-03 | `info` 命名空间 | 包含 `get_group_info` 等查询操作 |
| A-04 | `__getattr__` 兜底 | 未定义方法透传到底层 API |
### API 错误层级 (`test_api_errors.py`)

| 规范 ID | 说明 | 验证点 |
|---------|------|--------|
| AE-01 | `APIError` 构造 | 可用 `retcode` / `message` / `wording` 构造 |
| AE-02 | `retcode=0` 不抛异常 | `raise_for_retcode` 正常返回 |
| AE-03 | `retcode=1400` | 抛 `APIRequestError` |
| AE-04 | `retcode=1401` | 抛 `APIPermissionError` |
| AE-05 | `retcode=1404` | 抛 `APINotFoundError` |
| AE-06 | 未知 retcode | 抛基类 `APIError` |
| AE-07 | 继承关系 | 所有子类都是 `APIError` 实例 |
