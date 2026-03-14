"""
统一的 Bot API 类

使用依赖注入和组合模式整合所有 API 功能。
"""

from __future__ import annotations

from typing import Any, Callable, Coroutine, Dict, Optional, TYPE_CHECKING

from .client import IAPIClient, CallbackAPIClient
from .api_account import AccountAPI
from .api_group import GroupAPI
from .api_message import MessageAPI
from .api_private import PrivateAPI
from .api_support import SupportAPI

if TYPE_CHECKING:
    from ncatbot.core.service import ServiceManager


class BotAPI(AccountAPI, GroupAPI, MessageAPI, PrivateAPI, SupportAPI):
    """
    统一的 Bot API 类

    通过依赖注入整合所有 API 功能，提供完整的 Bot 操作接口。

    架构说明：
    - 使用多重继承组合各个 API 模块的功能
    - 所有 API 模块共享同一个 IAPIClient 实例
    - 支持依赖注入，方便测试和扩展

    使用方式：
    ```python
    # 使用回调函数创建（传统方式，向后兼容）
    api = BotAPI(adapter.send)

    # 使用 IAPIClient 创建（推荐方式）
    client = CallbackAPIClient(adapter.send)

    # 异步调用
    info = await api.get_login_info()

    ```

    Attributes:
        _client: API 客户端实例
    """

    def __init__(
        self,
        async_callback: Callable[
            [str, Optional[Dict[str, Any]]], Coroutine[Any, Any, Dict]
        ],
        service_manager: Optional["ServiceManager"] = None,
    ):
        """
        使用线程安全的异步回调函数初始化

        Args:
            async_callback: 线程安全的异步回调函数，接受 (endpoint, params) 返回响应字典，可以在任意线程调用
            service_manager: 服务管理器实例（可选）

        """
        # 将回调函数包装为 IAPIClient
        client = CallbackAPIClient(async_callback)

        # 初始化所有父类（使用 MRO 确保正确初始化）
        super().__init__(client, service_manager)

    # -------------------------------------------------------------------------
    # 属性访问器
    # -------------------------------------------------------------------------

    @property
    def client(self) -> IAPIClient:
        """获取 API 客户端实例"""
        return self._client

    # -------------------------------------------------------------------------
    # 便捷方法
    # -------------------------------------------------------------------------

    async def is_connected(self) -> bool:
        """
        检查 API 连接状态

        Returns:
            bool: 是否已连接

        Note:
            通过尝试获取登录信息来判断连接状态
        """
        try:
            await self.get_login_info()
            return True
        except Exception:
            return False
