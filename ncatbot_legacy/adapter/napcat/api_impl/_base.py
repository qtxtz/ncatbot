"""
NapCatBotAPI 基础类

提供协议调用、预上传等内部工具方法。
"""

from __future__ import annotations

import os
from typing import Any, Optional

from ncatbot.utils import get_log

from ..preupload import PreUploadService
from ..protocol import NapCatProtocol

LOG = get_log("NapCatBotAPI")


class NapCatBotAPIBase:
    """NapCatBotAPI 基础类，提供内部工具方法"""

    def __init__(self, protocol: NapCatProtocol, preupload: Optional[PreUploadService] = None):
        self._protocol = protocol
        self._preupload = preupload

    async def _call(self, action: str, params: Optional[dict] = None) -> dict:
        """发送 API 请求"""
        resp = await self._protocol.send(action, params)
        return resp

    async def _call_data(self, action: str, params: Optional[dict] = None) -> Any:
        """发送 API 请求并返回 data 字段"""
        resp = await self._call(action, params)
        return resp.get("data")

    async def _preupload_message(self, message: list) -> list:
        """预上传消息中的文件资源（NapCat 平台特有）"""
        if not self._preupload:
            return message
        result = await self._preupload.process_message_array(message)
        if result.success and result.data:
            return result.data.get("message", message)
        LOG.warning(f"消息预上传处理失败: {result.errors}")
        return message

    async def _preupload_file(self, file_value: str, file_type: str = "file") -> str:
        """预上传单个文件（NapCat 平台特有）"""
        if not self._preupload:
            if file_value and not file_value.startswith(
                ("http://", "https://", "base64://", "file://")
            ):
                if os.path.isabs(file_value) or os.path.exists(file_value):
                    return f"file://{os.path.abspath(file_value)}"
            return file_value
        try:
            return await self._preupload.preupload_file_if_needed(file_value, file_type)
        except Exception as e:
            LOG.warning(f"文件预上传失败: {e}，使用原始路径")
            if file_value and not file_value.startswith(
                ("http://", "https://", "base64://", "file://")
            ):
                if os.path.isabs(file_value) or os.path.exists(file_value):
                    return f"file://{os.path.abspath(file_value)}"
            return file_value
