"""
API 组件基类（依赖注入）
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TYPE_CHECKING

from ncatbot.utils import get_log

from .errors import NapCatAPIError

if TYPE_CHECKING:
    from ..client import IAPIClient, APIResponse
    from ncatbot.core.service import ServiceManager

LOG = get_log("API")


class APIComponent:
    """
    API 组件基类（使用依赖注入）

    所有 API 模块应继承此类，通过构造函数注入 IAPIClient 依赖。
    """

    def __init__(
        self, client: "IAPIClient", service_manager: Optional["ServiceManager"] = None
    ):
        """
        Args:
            client: API 客户端实例，实现 IAPIClient 接口
            service_manager: 服务管理器实例（可选）
        """
        self._client = client
        self._service_manager = service_manager

    @property
    def services(self) -> Optional["ServiceManager"]:
        """获取服务管理器实例"""
        return self._service_manager

    @property
    def _preupload_available(self) -> bool:
        """预上传服务是否可用"""
        if not self._service_manager:
            return False
        preupload = self._service_manager.preupload
        return preupload is not None and preupload.available

    async def _preupload_message(
        self, message: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        预上传消息中的文件资源

        Args:
            message: 消息段列表

        Returns:
            处理后的消息段列表
        """
        if not self._preupload_available:
            return message

        assert self._service_manager is not None
        preupload = self._service_manager.preupload
        result = await preupload.process_message_array(message)

        if result.success and result.data:
            return result.data.get("message", message)

        LOG.warning(f"消息预上传处理失败: {result.errors}")
        return message

    async def _preupload_file(
        self, file_value: str, file_type: str = "file", require_preupload: bool = False
    ) -> str:
        """
        预上传单个文件

        Args:
            file_value: 文件路径/URL/Base64
            file_type: 文件类型
            require_preupload: 是否必须使用预上传服务（为 True 时，服务不可用将报错）

        Returns:
            处理后的文件路径

        Raises:
            NapCatAPIError: 如果 require_preupload=True 且预上传服务不可用
        """
        import os

        if not self._preupload_available:
            if require_preupload:
                raise NapCatAPIError(
                    "预上传服务不可用。请确保：\n"
                    "1. PreUploadService 已注册\n"
                    "2. ServiceManager 已传入 BotAPI\n"
                    "3. 预上传服务已正确启动"
                )
            # 预上传服务不可用时，将本地路径转换为 file:// URL
            # NapCat 需要 file:// 协议的 URL 格式
            if file_value and not file_value.startswith(
                ("http://", "https://", "base64://", "file://")
            ):
                # 可能是本地路径
                if os.path.isabs(file_value) or os.path.exists(file_value):
                    abs_path = os.path.abspath(file_value)
                    return f"file://{abs_path}"
            return file_value

        try:
            assert self._service_manager is not None
            preupload = self._service_manager.preupload
            return await preupload.preupload_file_if_needed(file_value, file_type)
        except Exception as e:
            if require_preupload:
                raise NapCatAPIError(f"文件预上传失败: {e}") from e
            LOG.warning(f"文件预上传失败: {e}，使用原始路径")
            # 失败时也尝试转换为 file:// URL
            if file_value and not file_value.startswith(
                ("http://", "https://", "base64://", "file://")
            ):
                if os.path.isabs(file_value) or os.path.exists(file_value):
                    abs_path = os.path.abspath(file_value)
                    return f"file://{abs_path}"
            return file_value

    async def _request(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> "APIResponse":
        """
        发送 API 请求

        Args:
            endpoint: API 端点
            params: 请求参数

        Returns:
            APIResponse 对象
        """
        return await self._client.request(endpoint, params)

    async def _request_raw(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        发送 API 请求并返回原始字典

        为了兼容现有代码，返回原始响应字典。

        Args:
            endpoint: API 端点
            params: 请求参数

        Returns:
            原始响应字典
        """
        response = await self._client.request(endpoint, params)
        return response.raw
