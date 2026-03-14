"""
注册系统 (Registry)

Hook 驱动 + Dispatcher 分发 + Registrar 装饰器。

核心三件套:
- Hook: 绑定在 handler 上的拦截器 (BEFORE_CALL / AFTER_CALL / ON_ERROR)
- Dispatcher: 纯机械分发器，订阅 EventBus → 收集 handler → 执行 Hook 链
- Registrar: 无状态装饰器集合，标记 handler 并在 flush_pending 时注册到 Dispatcher

旧 RegistryEngine 已移至 ncatbot.legacy.registry，仅做过渡兼容。
"""

# Legacy RegistryEngine (过渡期保留)
from ncatbot.legacy.registry import RegistryEngine

# 导出全局注册表（从原 unified_registry 位置）
from ncatbot.core.service.builtin.unified_registry.filter_system import filter_registry
from ncatbot.core.service.builtin.unified_registry.filter_system.event_registry import (
    event_registry,
)
from ncatbot.core.service.builtin.unified_registry.command_system.registry.registry import (
    command_registry,
)

# 导出装饰器 API (legacy, 仍在过渡期使用)
from ncatbot.core.service.builtin.unified_registry.filter_system.decorators import *  # noqa: F401,F403
from ncatbot.core.service.builtin.unified_registry.command_system.registry import (
    option,
    param,
    option_group,
)

# Hook 系统
from .hook import Hook, HookStage, HookAction, HookContext, add_hooks, get_hooks

# 内置 Hook
from .builtin_hooks import (
    MessageTypeFilter,
    PostTypeFilter,
    SubTypeFilter,
    SelfFilter,
    group_only,
    private_only,
    non_self,
)

# Dispatcher
from .dispatcher import Dispatcher as HandlerDispatcher, HandlerEntry

# Registrar
from .registrar import Registrar, registrar, flush_pending

__all__ = [
    # Legacy (过渡)
    "RegistryEngine",
    "command_registry",
    "filter_registry",
    "event_registry",
    "option",
    "param",
    "option_group",
    # Hook
    "Hook",
    "HookStage",
    "HookAction",
    "HookContext",
    "add_hooks",
    "get_hooks",
    # 内置 Hook
    "MessageTypeFilter",
    "PostTypeFilter",
    "SubTypeFilter",
    "SelfFilter",
    "group_only",
    "private_only",
    "non_self",
    # Dispatcher
    "HandlerDispatcher",
    "HandlerEntry",
    # Registrar
    "Registrar",
    "registrar",
    "flush_pending",
]
