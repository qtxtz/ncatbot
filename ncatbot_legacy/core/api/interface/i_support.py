"""
IBotAPI 支持功能接口

声明所有辅助功能相关的异步接口方法。
"""

from abc import ABC, abstractmethod
from typing import Any, List, Literal, Union


class ISupportAPI(ABC):
    """支持功能操作接口

    包含：AI 声聊、状态检查、OCR、版本信息等。
    """

    # ==================================================================
    # AI 声聊
    # ==================================================================

    @abstractmethod
    async def get_ai_characters(
        self,
        group_id: Union[str, int],
        chat_type: Literal[1, 2],
    ) -> Any:
        """获取 AI 声聊角色列表"""

    @abstractmethod
    async def get_ai_record(
        self,
        group_id: Union[str, int],
        character_id: str,
        text: str,
    ) -> str:
        """获取 AI 声聊语音"""

    # ==================================================================
    # 状态检查
    # ==================================================================

    @abstractmethod
    async def can_send_image(self) -> bool:
        """检查是否可以发送图片"""

    @abstractmethod
    async def can_send_record(self, group_id: Union[str, int]) -> bool:
        """检查是否可以发送语音"""

    # ==================================================================
    # OCR
    # ==================================================================

    @abstractmethod
    async def ocr_image(self, image: str) -> List[dict]:
        """图片文字识别（OCR）"""

    # ==================================================================
    # 系统
    # ==================================================================

    @abstractmethod
    async def get_version_info(self) -> dict:
        """获取版本信息"""

    @abstractmethod
    async def bot_exit(self) -> None:
        """退出机器人"""
