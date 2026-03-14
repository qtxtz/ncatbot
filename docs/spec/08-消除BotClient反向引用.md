# SPEC-08: 消除 BotClient 反向引用

## 1. 问题陈述

当前多个子系统通过 `services.bot_client` 或 `self._bot_client` 反向持有完整的 `BotClient` 引用，形成循环依赖：

```
BotClient → ServiceManager → bot_client → BotClient
BotClient → PluginLoader → ServiceManager → bot_client → BotClient
```

这导致：
- 子系统无法独立测试（必须构造完整 BotClient）
- BotClient 成为隐式的上帝对象（所有子系统都能通过它访问其它任何子系统）
- 新需求倾向于继续往 BotClient 上挂属性，加速耦合膨胀

## 2. 现状：反向引用调用清单

下表列出所有通过 `bot_client` 反向引用的调用点，以及它们**实际需要的最小能力**：

| # | 调用方 | 调用路径 | 实际需要 | 分类 |
|---|--------|----------|----------|------|
| A1 | `PluginLoader._load_plugin_by_class()` | `services.bot_client.api` | 获取 `IBotAPI` 实例 | API 注入 |
| A2 | `PluginLoader.load_plugin()` | `services.bot_client.registry_engine.set_current_plugin_name()` | Legacy 注册上下文设置 | Legacy |
| B1 | `NcatBotPlugin.__onload__()` | `services.bot_client.registry_engine.handle_plugin_load()` | Legacy 命令注册刷新 | Legacy |
| B2 | `NcatBotPlugin.__onload__()` | `services.bot_client.handler_dispatcher` → `flush_pending()` | 把 pending handler 注册到 Dispatcher | Handler 注册 |
| B3 | `NcatBotPlugin.__unload__()` | `services.bot_client.registry_engine.handle_plugin_unload()` | Legacy 命令注销 | Legacy |
| B4 | `NcatBotPlugin.__unload__()` | `services.bot_client.handler_dispatcher.revoke_plugin()` | 撤销插件的 handler | Handler 注册 |
| C1 | `CommandRunner.run()` | `bot_client.get_plugin_class_by_name()` | 根据插件名获取插件类 | 插件查询 |
| C2 | `CommandRunner.run()` | `bot_client.get_plugin()` | 根据类型获取插件实例 | 插件查询 |
| D1 | `RegistryEngine._get_plugin_instance()` | `self._bot_client.get_plugin_class_by_name()` | 同 C1 | 插件查询 |
| D2 | `RegistryEngine._get_plugin_instance()` | `self._bot_client.get_plugin()` | 同 C2 | 插件查询 |
| E1 | `SystemManager._handle_unified_registry_message()` | `services.bot_client.registry_engine` | Legacy 桥接 | Legacy |
| E2 | `SystemManager._handle_unified_registry_legacy()` | `services.bot_client.registry_engine` | Legacy 桥接 | Legacy |
| F1 | `ServiceManager.event_bus` (属性) | `self._bot_client.event_bus` | 获取 EventBus | 已有替代方案 |
| F2 | `BaseService.event_bus` (属性) | `self.service_manager._bot_client.event_bus` | 获取 EventBus | 已有替代方案 |

## 3. 设计原则

- **最小接口原则**：每个消费方只拿到它需要的最小接口（Protocol），不接触完整 BotClient。
- **单向依赖**：BotClient → 子系统，子系统之间通过接口通信，不反向引用 BotClient。
- **渐进式迁移**：每步可独立合并，不需要一次性改完所有调用点。

## 4. 接口设计

### 4.1 `IPluginRegistry` — 插件查询协议

解决 C1/C2/D1/D2 四个调用点。

```python
# ncatbot/core/api/protocols.py (新文件)

from typing import Protocol, Type, TypeVar, List, Optional, TYPE_CHECKING, runtime_checkable

if TYPE_CHECKING:
    from ncatbot.plugin_system.base_plugin import BasePlugin

T = TypeVar("T")


@runtime_checkable
class IPluginRegistry(Protocol):
    """插件查询能力的最小接口"""

    def get_plugin(self, plugin_type: Type[T]) -> T:
        """按类型获取插件实例"""
        ...

    def get_plugin_class_by_name(self, plugin_name: str) -> Type["BasePlugin"]:
        """按名称获取插件类"""
        ...

    def get_registered_plugins(self) -> List["BasePlugin"]:
        """获取已注册的插件列表"""
        ...
```

**消费方改造**：
- `CommandRunner.__init__()` 接收 `plugin_registry: IPluginRegistry` 参数
- `RegistryEngine.set_plugin_registry(registry: IPluginRegistry)` 替代 `set_bot_client()`
- `BotClient` 在 `_setup_api()` 中将自身（它已经实现了这三个方法）作为 `IPluginRegistry` 注入

### 4.2 `IHandlerDispatcher` — Handler 注册/清理协议

解决 B2/B4 两个调用点。

```python
# 同 protocols.py

from typing import Protocol, Callable, Any


class IHandlerDispatcher(Protocol):
    """Handler 注册/清理能力的最小接口"""

    def register_handler(
        self,
        event_type: str,
        func: Callable,
        priority: int = 0,
        plugin_name: str = "",
        **metadata: Any,
    ) -> Any:
        ...

    def revoke_plugin(self, plugin_name: str) -> int:
        ...
```

**消费方改造**：
- `NcatBotPlugin` 通过 `services.handler_dispatcher` 访问（ServiceManager 新增属性）
- `flush_pending()` 函数签名：`flush_pending(dispatcher: IHandlerDispatcher, plugin_name: str)`（已满足，当前参数类型是 `Dispatcher`）

### 4.3 `ILegacyRegistry` — Legacy 兼容协议

解决 A2/B1/B3/E1/E2 五个调用点。过渡期使用，Legacy 移除后整体删除。

```python
# 同 protocols.py

from typing import Protocol


class ILegacyRegistry(Protocol):
    """Legacy RegistryEngine 的最小接口（过渡期）"""

    def set_current_plugin_name(self, name: str) -> None: ...
    def handle_plugin_load(self) -> None: ...
    def handle_plugin_unload(self, name: str) -> None: ...
    async def handle_message_event(self, event) -> None: ...
    async def handle_legacy_event(self, event) -> None: ...
```

### 4.4 IBotAPI 直接注入

解决 A1。当前路径为 `services.bot_client.api`。

**改造方案**：`ServiceManager` 增加 `api` 属性，由 BotClient 在 `_setup_api()` 中直接设置：

```python
# ServiceManager 新增
@property
def api(self) -> "IBotAPI":
    return self._api

def set_api(self, api: "IBotAPI") -> None:
    self._api = api
```

`PluginLoader` 改为 `self._service_manager.api`。

### 4.5 EventBus 直接注入（F1/F2 — 已有替代路径）

当前 `ServiceManager.__init__` 已接受 `event_bus` 参数，F1/F2 只是在 `event_bus=None` 时的 fallback。

**改造方案**：确保 `ServiceManager` 构造时必传 `event_bus`，移除 `_bot_client.event_bus` 的 fallback 路径。

## 5. ServiceManager 改造后的属性表

| 属性 | 类型 | 注入时机 | 替代的旧路径 |
|------|------|----------|-------------|
| `event_bus` | `EventBus` | 构造时传入 | `_bot_client.event_bus` |
| `api` | `IBotAPI` | `set_api()` | `_bot_client.api` |
| `handler_dispatcher` | `IHandlerDispatcher` | `set_handler_dispatcher()` | `_bot_client.handler_dispatcher` |
| `legacy_registry` | `ILegacyRegistry` (可选) | `set_legacy_registry()` | `_bot_client.registry_engine` |
| `plugin_registry` | `IPluginRegistry` (可选) | `set_plugin_registry()` | `_bot_client.get_plugin()` 等 |

**移除**：`set_bot_client()` 和 `_bot_client` 属性。

## 6. 迁移步骤

### Phase 1: 定义协议 + 新增注入口（纯增量，无破坏性）

1. 创建 `ncatbot/core/protocols.py`，定义 `IPluginRegistry` / `IHandlerDispatcher` / `ILegacyRegistry`。
2. `ServiceManager` 新增 `api` / `handler_dispatcher` / `legacy_registry` / `plugin_registry` 属性及对应 setter。
3. `BotClient.__init__` 和 `_setup_api()` 中调用新 setter 注入各接口。
4. 此阶段 `set_bot_client()` 保留不动，新旧路径并存。

### Phase 2: 逐个消费方切换（可逐文件合并）

每个消费方独立切换，互不依赖：

| 文件 | 改动 |
|------|------|
| `plugin_system/loader/core.py` | `services.bot_client.api` → `services.api` |
| `plugin_system/loader/core.py` | `services.bot_client.registry_engine.set_current_plugin_name()` → `services.legacy_registry.set_current_plugin_name()` |
| `plugin_system/builtin_mixin/ncatbot_plugin.py` | `services.bot_client.handler_dispatcher` → `services.handler_dispatcher` |
| `plugin_system/builtin_mixin/ncatbot_plugin.py` | `services.bot_client.registry_engine.xxx()` → `services.legacy_registry.xxx()` |
| `plugin_system/builtin_plugin/system_manager.py` | `services.bot_client.registry_engine` → `services.legacy_registry` |
| `core/service/builtin/unified_registry/command_runner.py` | `bot_client` 参数 → `plugin_registry: IPluginRegistry` 参数 |
| `legacy/registry/engine.py` | `self._bot_client` → `self._plugin_registry: IPluginRegistry` |
| `legacy/registry/command_runner.py` | 同上 |
| `core/service/manager.py` | 移除 `_bot_client.event_bus` 的 fallback |
| `core/service/base.py` | 移除 `service_manager._bot_client.event_bus` 的 fallback |

### Phase 3: 移除旧路径

1. 删除 `ServiceManager.set_bot_client()` / `_bot_client` / `bot_client` 属性。
2. 删除 `RegistryEngine.set_bot_client()`。
3. 删除 `BotClient` 中的 `self.services.set_bot_client(self)` 和 `self.registry_engine.set_bot_client(self)`。

### Phase 4: Legacy 移除后清理

Legacy RegistryEngine 完全移除时：
1. 删除 `ILegacyRegistry` 协议。
2. 删除 `ServiceManager.legacy_registry` 属性。
3. 删除 `BotClient` 中的 `registry_engine`、`_on_message_for_registry`、`_on_legacy_for_registry`。
4. 删除 `SystemManager` 中的桥接方法。

## 7. BotClient 改造前后对比

### 改造前

```python
class BotClient(LifecycleManager):
    def __init__(self):
        self.event_bus = EventBus()
        self.registry_engine = RegistryEngine()
        self.handler_dispatcher = HandlerDispatcher(self.event_bus)
        self.services = ServiceManager(event_bus=self.event_bus)
        self.services.set_bot_client(self)          # ← 双向引用
        ...

    async def _setup_api(self):
        self.api = self.adapter.get_api()
        self.dispatcher = EventDispatcher(self.event_bus, self.api, services=self.services)
        self.adapter.set_event_callback(self.dispatcher.dispatch)
        self.registry_engine.set_bot_client(self)   # ← 双向引用
```

### 改造后

```python
class BotClient(LifecycleManager):
    def __init__(self):
        self.event_bus = EventBus()
        self.registry_engine = RegistryEngine()
        self.handler_dispatcher = HandlerDispatcher(self.event_bus)
        self.services = ServiceManager(event_bus=self.event_bus)

        # 注入独立接口，无双向引用
        self.services.set_handler_dispatcher(self.handler_dispatcher)
        self.services.set_legacy_registry(self.registry_engine)
        ...

    async def _setup_api(self):
        self.api = self.adapter.get_api()
        self.dispatcher = EventDispatcher(self.event_bus, self.api, services=self.services)
        self.adapter.set_event_callback(self.dispatcher.dispatch)

        # 注入 API 和插件查询能力
        self.services.set_api(self.api)
        self.services.set_plugin_registry(self)
        self.registry_engine.set_plugin_registry(self)
```

## 8. 依赖图对比

### 改造前

```
BotClient ──→ ServiceManager ──→ bot_client ──→ BotClient (循环)
BotClient ──→ PluginLoader ──→ ServiceManager ──→ bot_client ──→ BotClient (循环)
BotClient ──→ RegistryEngine ──→ bot_client ──→ BotClient (循环)
```

### 改造后

```
BotClient ──→ ServiceManager ──→ IHandlerDispatcher (接口)
                               ──→ ILegacyRegistry (接口, 过渡)
                               ──→ IPluginRegistry (接口)
                               ──→ IBotAPI (接口)
                               ──→ EventBus (直接注入)

BotClient ──→ RegistryEngine ──→ IPluginRegistry (接口)

所有箭头单向，无循环。
```

## 9. 验收标准

- [ ] `ServiceManager` 不再持有 `_bot_client` 属性
- [ ] `RegistryEngine` 不再持有 `_bot_client` 属性
- [ ] `grep -r "bot_client" ncatbot/` 仅出现在 `BotClient` 类自身和 MCP 模块中
- [ ] 所有子系统可通过 mock 接口独立实例化和测试
- [ ] 现有功能不受影响（插件加载、命令执行、热重载均正常）

## 10. 风险与注意事项

| 风险 | 缓解 |
|------|------|
| `IPluginRegistry` 在 `_setup_api()` 之前不可用 | `PluginLoader` 在 `_core_execution` Step 6 才使用，此时 Step 5 已完成注入 |
| Legacy 调用点多 | Phase 2 逐文件切换，每步可独立验证 |
| `BotClient` 实现 `IPluginRegistry` 是否合理 | 合理——BotClient 持有 `plugin_loader`，本身就是 Composition Root，实现查询协议是自然的委托 |
