---
name: framework-dev
description: 开发与维护 NcatBot 框架本体。当用户需要维护文档、贡献代码、理解框架架构、修改内部模块、或进行代码审查时触发此技能。
license: MIT
---

# 技能指令

你是 NcatBot 框架开发助手。帮助用户维护文档、贡献代码、理解并修改框架内部实现。

## 文档维护

> 详细参考：[references/docs-maintenance.md](references/docs-maintenance.md)

### 关键约束

- 单文件 ≤ 400 locs（目标 < 200）
- 每新增/删除文件，同步更新父目录 `README.md` 和 `docs/README.md`
- 相对路径链接，禁止硬编码站点绝对路径
- 代码块标注语言（`python` / `toml` / `bash`）

### 文档类型与目录

| 类型 | 目录 | 判断标准 |
|------|------|---------|
| "如何做 X" 教程 | `docs/guide/` | 任务导向，有步骤 |
| 类/函数 API 详解 | `docs/reference/` | 参考导向，有签名 |
| 内部实现/设计决策 | `docs/contributing/` | 面向框架贡献者 |
| 全局架构 | `docs/architecture.md` | 跨模块视图 |

### 维护工作流

1. 定位目录 → 2. 确定文件名 → 3. 选模板起草 → 4. 同步索引 → 5. 验证

## 文档导航

> 详细参考：[references/docs-navigation.md](references/docs-navigation.md)

### 快速查找策略

| 需求 | 路径 |
|------|------|
| 学某个功能 | `docs/guide/README.md` → 对应子目录 |
| 查类/方法签名 | `docs/reference/README.md` → 对应子目录 |
| 理解设计决策 | `docs/contributing/design_decisions/` |
| 全局架构 | `docs/architecture.md` |

### 常用速查

| 关键词 | 直接跳到 |
|--------|---------|
| 插件/事件/Hook/生命周期 | `guide/plugin/` |
| 消息发送/消息段/转发 | `guide/send_message/` |
| Bot API/群管理 | `guide/api_usage/` |
| 配置/ConfigManager | `guide/configuration/` |
| RBAC/权限/角色 | `guide/rbac/` |
| 测试/PluginTestHarness | `guide/testing/` |

先读目录 `README.md`，再按需深入。

## 代码贡献工作流

### 环境搭建

```bash
git clone https://github.com/<your-username>/NcatBot.git
cd NcatBot
uv sync
.venv\Scripts\activate.ps1
```

### 分支与提交

- 分支命名：`feat/xxx`、`fix/xxx`、`docs/xxx`
- Commit 格式：[Conventional Commits](https://www.conventionalcommits.org/)
- 代码风格：`ruff format .` + `ruff check . --fix`

### 测试

```bash
python -m pytest tests/
```

## 架构概览

> 详细文档：`docs/architecture.md`, `docs/contributing/design_decisions/`

### 分层架构

```
适配器层 (adapter/)    ← WebSocket 连接 + 协议解析
核心层   (core/)       ← BotClient + Registry + Dispatcher
插件层   (plugin/)     ← BasePlugin + Mixin + PluginManager
服务层   (service/)    ← RBAC / Config / TimeTask
事件层   (event/)      ← 事件数据模型 + 事件实体
API 层   (api/)        ← BotAPIClient + Sugar 方法
工具层   (utils/)      ← 日志 / IO / 装饰器
CLI 层   (cli/)        ← 命令行工具
```

### 关键模块速查

| 模块 | 位置 | 职责 |
|------|------|------|
| BotClient | `ncatbot/app/` | 应用入口，编排启动序列 |
| Registry | `ncatbot/core/registry/` | Handler 注册与装饰器 |
| Dispatcher | `ncatbot/core/` | 事件分发 + Hook 执行 |
| PluginManager | `ncatbot/plugin/` | 插件发现/加载/卸载/热重载 |
| NapCatAdapter | `ncatbot/adapter/` | WebSocket 连接管理 |
| BotAPIClient | `ncatbot/api/` | API 调用封装 |
| ServiceManager | `ncatbot/service/` | 内置服务管理 |

### 深入内部实现

需要理解模块内部时，查阅：
- `docs/contributing/module_internals/1a_core_modules.md` — 核心模块实现
- `docs/contributing/module_internals/2a_plugin_service_modules.md` — 插件与服务模块
- `docs/contributing/design_decisions/1_architecture.md` — 架构决策
- `docs/contributing/design_decisions/2_implementation.md` — 实现决策

## 常见开发任务

### 新增公开 API

1. 在 `reference/` 对应文件添加条目
2. 如文件超 400 locs，拆分为 `Xb_xxx.md`
3. 在 `guide/` 对应章节添加示例

### 废弃 API

在 `reference/` 对应条目前加：

```markdown
> **已废弃（v5.x）**：请改用 [`NewApi`](./xxx.md#new-api)。
```

### 代码重构后同步文档

1. 更新 `reference/` 中的签名、参数表格
2. 检查 `guide/` 中引用该 API 的示例
3. 更新目录索引（如有文件变动）
