"""
兼容层：EventRegistry 已移至 ncatbot.legacy.client.registry

.. deprecated::
    请使用 ncatbot.core.registry.Registrar 替代。
"""

import warnings

warnings.warn(
    "ncatbot.core.client.registry.EventRegistry 已废弃，"
    "请使用 ncatbot.core.registry.Registrar 替代。",
    DeprecationWarning,
    stacklevel=2,
)

from ncatbot.legacy.client.registry import EventRegistry  # noqa: F401

__all__ = ["EventRegistry"]
