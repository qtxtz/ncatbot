"""
API 参数验证工具
"""

from __future__ import annotations

from typing import Any, List

from .errors import APIValidationError


def require_at_least_one(*args: Any, names: List[str]) -> None:
    """
    要求至少提供一个参数

    Args:
        *args: 参数值列表
        names: 对应的参数名称列表

    Raises:
        APIValidationError: 如果所有参数都为 None
    """
    if all(arg is None for arg in args):
        raise APIValidationError(f"至少需要提供以下参数之一: {', '.join(names)}")


def require_exactly_one(*args: Any, names: List[str]) -> None:
    """
    要求恰好提供一个参数

    Args:
        *args: 参数值列表
        names: 对应的参数名称列表

    Raises:
        APIValidationError: 如果提供的参数数量不是 1
    """
    count = sum(1 for arg in args if arg is not None)
    if count != 1:
        raise APIValidationError(f"必须且只能提供以下参数之一: {', '.join(names)}")


def check_exclusive_argument(*args: Any, names: List[str], error: bool = False) -> bool:
    """
    检查互斥参数，确保只提供一个

    Args:
        *args: 参数值列表
        names: 对应的参数名称列表
        error: 如果为 True，在检查失败时抛出异常

    Returns:
        bool: 如果恰好提供一个参数返回 True，否则返回 False

    Raises:
        APIValidationError: 如果 error=True 且提供的参数数量不是 1
    """
    count = sum(1 for arg in args if arg is not None)
    if count != 1:
        if error:
            raise APIValidationError(f"必须且只能提供以下参数之一: {', '.join(names)}")
        return False
    return True
