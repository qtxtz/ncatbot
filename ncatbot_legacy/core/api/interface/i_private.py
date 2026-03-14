"""
IBotAPI 私聊接口

声明所有私聊相关的异步接口方法。
"""

from abc import ABC, abstractmethod
from typing import Any, Optional, Union


class IPrivateAPI(ABC):
    """私聊操作接口

    包含：私聊文件上传/下载、输入状态等。
    """

    # ==================================================================
    # 文件操作
    # ==================================================================

    @abstractmethod
    async def upload_private_file(
        self,
        user_id: Union[str, int],
        file: str,
        name: str,
    ) -> None:
        """上传私聊文件"""

    @abstractmethod
    async def get_private_file_url(self, file_id: str) -> str:
        """获取私聊文件下载链接"""

    # ==================================================================
    # 输入状态
    # ==================================================================

    @abstractmethod
    async def set_input_status(
        self, event_type: int, user_id: Union[str, int]
    ) -> None:
        """设置输入状态"""
