"""
API 错误类型定义
"""

from __future__ import annotations

from typing import Optional

from ncatbot.utils import get_log, NcatBotError

LOG = get_log("API")


class NapCatAPIError(Exception):
    """NapCat API 调用错误"""

    def __init__(self, info: str, retcode: Optional[int] = None):
        LOG.error(f"NapCatAPIError: {info}")
        self.info = info
        self.retcode = retcode
        super().__init__(info)


class APIValidationError(NcatBotError):
    """API 参数验证错误"""

    logger = LOG

    def __init__(self, message: str):
        super().__init__(f"参数验证失败: {message}")
