# Adapter 模块测试

源码模块: `ncatbot.adapter.napcat`

## 验证规范

### EventParser (`test_event_parser.py`)

测试 `EventParser` 注册表、路由推导、OB11 JSON 解析及 `NapCatEventParser` 包装器。

| 规范 ID | 说明 | 验证点 |
|---------|------|--------|
| P-01 | 注册表完整性 | `_registry` 包含全部 17 种内置事件类型 |
| P-02 | `_get_key()` 推导 | message/notice/request/meta_event 各 post_type 正确路由 |
| P-03 | `parse()` 解析真实 OB11 JSON | 私聊/群聊/心跳/生命周期/戳一戳/好友请求/群撤回/禁言/群增 |
| P-04 | 错误处理 | 缺失/未知 post_type → `ValueError` |
| P-05 | NapCatEventParser 包装器 | 缺 post_type → `None`，未知类型 → `None` |
| P-06 | message_sent 映射 | `message_sent` 映射到 `MESSAGE` + `message_type` |
| P-07 | notify 子类型推导 | `notice_type=notify` 时使用 `sub_type` 推导 |

## 运行方式

```bash
# 运行全部 adapter 测试
python -m pytest tests/unit/adapter/ -v
```

### AdapterRegistry (`test_registry.py`)

测试适配器注册表的注册、发现、创建、列举和错误处理。

| 规范 ID | 说明 | 验证点 |
|---------|------|--------|
| AR-01 | `register()` + `discover()` | 注册后可通过 `discover()` 发现 |
| AR-02 | `list_available()` | 返回所有已注册适配器名称 |
| AR-03 | `create()` | 根据 AdapterEntry 创建适配器实例 |
| AR-04 | `create()` platform 覆盖 | `platform` 参数覆盖默认值 |
| AR-05 | 未知类型 | 抛 `ValueError` |
