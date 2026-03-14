"""
Legacy 注册系统

已废弃，将在未来版本移除。
请使用 ncatbot.core.registry (Hook + Dispatcher + Registrar) 替代。
"""

from .engine import RegistryEngine

__all__ = ["RegistryEngine"]
