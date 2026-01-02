"""统一注册模块

提供过滤器和命令的统一注册功能。
装饰器从 core/service/builtin/unified_registry 导出。
"""

from .plugin import UnifiedRegistryPlugin

# 从服务模块导出装饰器和注册器
from ncatbot.core.service.builtin.unified_registry import (
    filter_registry,
    command_registry,
    option,
    param,
    option_group,
)
from ncatbot.core.service.builtin.unified_registry.filter_system import *  # noqa: F401,F403
from ncatbot.core.service.builtin.unified_registry.filter_system.decorators import *  # noqa: F401,F403

__all__ = [
    "UnifiedRegistryPlugin",
    "command_registry",
    "filter_registry",
    "option",
    "param",
    "option_group",
]

from ncatbot.core.service.builtin.unified_registry import filter_system
__all__.extend(getattr(filter_system, "__all__", []))  # type: ignore
