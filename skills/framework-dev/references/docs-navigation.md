# 文档导航策略

## 文档全景

| 目录/文件 | 用途 | 优先查阅时机 |
|-----------|------|-------------|
| `architecture.md` | 系统架构 | 整体设计、模块交互 |
| `guide/` | 任务导向教程 | "如何做 X" |
| `reference/` | 完整 API 参考 | 函数签名、参数、返回值 |
| `contributing/` | 内部实现与设计 | 框架内部、参与开发 |

## 按问题类型选路径

### A：学某个功能（"如何..."）

`guide/README.md` → 找子目录 → 子目录 `README.md` → 目标文档

| 关键词 | 直接跳到 |
|--------|---------|
| 插件/Plugin/事件/Hook | `guide/plugin/` |
| 消息/图片/语音/转发 | `guide/send_message/` |
| Bot API/群管理 | `guide/api_usage/` |
| 配置/ConfigManager | `guide/configuration/` |
| 权限/RBAC/角色 | `guide/rbac/` |
| 测试/PluginTestHarness | `guide/testing/` |

### B：查类/方法签名

`reference/README.md` → 找子目录 → 目标文档

| 查找对象 | 文档位置 |
|----------|----------|
| BotClient / Registry / Dispatcher | `reference/core/1_internals.md` |
| 发消息 API | `reference/api/1a_message_api.md` / `1b_message_api.md` |
| 群管理 API | `reference/api/2_manage_api.md` |
| 查询/辅助 API | `reference/api/3_info_support_api.md` |
| 消息段类型 | `reference/types/1_segments.md` |
| MessageArray | `reference/types/2_message_array.md` |
| 事件类层级 | `reference/events/1_event_classes.md` |
| NcatBotPlugin | `reference/plugin/1_base_class.md` |
| Mixin 体系 | `reference/plugin/2_mixins.md` |
| RBAC 服务 | `reference/services/1_rbac_service.md` |
| 配置/定时任务服务 | `reference/services/2_config_task_service.md` |
| WebSocket 连接 | `reference/adapter/1_connection.md` |
| 协议解析 | `reference/adapter/2_protocol.md` |
| IO/日志工具 | `reference/utils/1a_io_logging.md` |
| 装饰器/杂项 | `reference/utils/2_decorators_misc.md` |
| TestHarness | `reference/testing/1_harness.md` |

### C：理解设计决策

| 关键词 | 文档位置 |
|--------|----------|
| 分层架构/适配器模式 | `contributing/design_decisions/1_architecture.md` |
| Dispatcher/Hook/热重载 | `contributing/design_decisions/2_implementation.md` |
| 核心模块实现 | `contributing/module_internals/1a_core_modules.md` |
| 插件/服务实现 | `contributing/module_internals/2a_plugin_service_modules.md` |

### D：全局架构

直接读 `architecture.md`。

## 高效阅读技巧

1. **先读 README.md**：每个目录的 README 包含概览和索引
2. **有序文件从第 1 篇开始**：带数字前缀的文件有依赖关系
3. **指南与参考互补**：`guide/` = 怎么用，`reference/` = 有什么参数
4. **跟随链接追踪**：文档末尾的"延伸阅读"是精选链接

## 减少读取量

1. `docs/README.md` 目录树是全局索引
2. 先读 README，再按需深入
3. 参考文档先看文件顶部签名
4. 每篇开头 `>` 引用块是一句话摘要
