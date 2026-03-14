"""
API 响应状态处理
"""

from __future__ import annotations

from typing import Any, Dict

from .errors import NapCatAPIError


class APIReturnStatus:
    """API 返回状态封装"""

    retcode: int
    message: str
    data: Any
    _raw: Dict[str, Any]

    def __init__(self, data: Dict[str, Any]):
        """
        从响应字典构造状态对象

        Args:
            data: API 响应字典

        Raises:
            NapCatAPIError: 如果响应表示失败
        """
        self.raise_if_failed(data)
        self.retcode = data.get("retcode", -1)
        self.message = data.get("message", "")
        self.data = data.get("data")
        self._raw = data

    @classmethod
    def raise_if_failed(cls, data: Dict[str, Any]) -> None:
        """
        检查响应是否成功，失败则抛出异常

        Args:
            data: API 响应字典

        Raises:
            NapCatAPIError: 如果 retcode != 0
        """
        if data.get("retcode") != 0:
            raise NapCatAPIError(
                data.get("message", "Unknown error"),
                retcode=data.get("retcode"),
            )

    @property
    def is_success(self) -> bool:
        return self.retcode == 0

    def __bool__(self) -> bool:
        return self.is_success

    def __str__(self) -> str:
        return f"APIReturnStatus(retcode={self.retcode}, message={self.message})"


class MessageAPIReturnStatus(APIReturnStatus):
    """消息 API 返回状态，包含 message_id"""

    @property
    def message_id(self) -> str:
        """获取消息 ID"""
        if self.data and "message_id" in self.data:
            return str(self.data["message_id"])
        return ""
