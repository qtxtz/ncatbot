"""
IBotAPI 消息接口

声明所有消息相关的异步接口方法。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Literal, Optional, Union


class IMessageAPI(ABC):
    """消息操作接口

    包含：消息发送/撤回、转发、表情、戳一戳、音乐等。
    """

    # ==================================================================
    # 基础消息操作
    # ==================================================================

    @abstractmethod
    async def send_private_msg(
        self, user_id: Union[str, int], message: list, **kwargs
    ) -> Any:
        """发送私聊消息"""

    @abstractmethod
    async def send_group_msg(
        self, group_id: Union[str, int], message: list, **kwargs
    ) -> Any:
        """发送群聊消息"""

    @abstractmethod
    async def delete_msg(self, message_id: Union[str, int]) -> None:
        """撤回消息"""

    # ==================================================================
    # 消息表情
    # ==================================================================

    @abstractmethod
    async def set_msg_emoji_like(
        self,
        message_id: Union[str, int],
        emoji_id: Union[str, int],
        set: bool = True,
    ) -> None:
        """消息贴表情"""

    # ==================================================================
    # 单条消息转发
    # ==================================================================

    @abstractmethod
    async def forward_group_single_msg(
        self,
        group_id: Union[str, int],
        message_id: Union[str, int],
    ) -> None:
        """向群转发单条消息"""

    @abstractmethod
    async def forward_private_single_msg(
        self,
        user_id: Union[str, int],
        message_id: Union[str, int],
    ) -> None:
        """向私聊转发单条消息"""

    # ==================================================================
    # 合并转发消息
    # ==================================================================

    @abstractmethod
    async def send_forward_msg(
        self,
        group_id: Optional[Union[str, int]] = None,
        user_id: Optional[Union[str, int]] = None,
        messages: Optional[list] = None,
        news: Optional[List[str]] = None,
        prompt: Optional[str] = None,
        summary: Optional[str] = None,
        source: Optional[str] = None,
    ) -> Any:
        """发送合并转发消息"""

    @abstractmethod
    async def send_group_forward_msg(
        self,
        group_id: Union[str, int],
        messages: List[dict],
        news: List[str],
        prompt: str,
        summary: str,
        source: str,
    ) -> Any:
        """发送群合并转发消息"""

    @abstractmethod
    async def send_private_forward_msg(
        self,
        user_id: Union[str, int],
        messages: List[dict],
        news: List[str],
        prompt: str,
        summary: str,
        source: str,
    ) -> Any:
        """发送私聊合并转发消息"""

    # ==================================================================
    # 消息获取
    # ==================================================================

    @abstractmethod
    async def get_msg(self, message_id: Union[str, int]) -> Any:
        """获取消息详情"""

    @abstractmethod
    async def get_forward_msg(self, message_id: Union[str, int]) -> Any:
        """获取合并转发消息内容"""

    @abstractmethod
    async def get_group_msg_history(
        self,
        group_id: Union[str, int],
        message_seq: Optional[Union[str, int]] = None,
        count: int = 20,
        reverse_order: bool = False,
    ) -> Any:
        """获取群消息历史"""

    @abstractmethod
    async def get_friend_msg_history(
        self,
        user_id: Union[str, int],
        message_seq: Union[str, int],
        count: int = 20,
        reverse_order: bool = False,
    ) -> Any:
        """获取好友消息历史"""

    @abstractmethod
    async def get_record(
        self,
        file: Optional[str] = None,
        file_id: Optional[str] = None,
        out_format: Literal[
            "mp3", "amr", "wma", "m4a", "ogg", "wav", "flac", "spx"
        ] = "mp3",
    ) -> Any:
        """获取语音文件"""

    @abstractmethod
    async def get_image(
        self,
        file: Optional[str] = None,
        file_id: Optional[str] = None,
    ) -> Any:
        """获取图片文件"""

    @abstractmethod
    async def fetch_emoji_like(
        self,
        message_id: Union[str, int],
        emoji_id: Union[str, int],
        emoji_type: Union[str, int],
    ) -> dict:
        """获取贴表情详情"""

    # ==================================================================
    # 戳一戳
    # ==================================================================

    @abstractmethod
    async def send_poke(
        self,
        user_id: Union[str, int],
        group_id: Optional[Union[str, int]] = None,
    ) -> None:
        """发送戳一戳"""

    @abstractmethod
    async def group_poke(
        self,
        group_id: Union[str, int],
        user_id: Union[str, int],
    ) -> None:
        """群内戳一戳"""

    @abstractmethod
    async def friend_poke(self, user_id: Union[str, int]) -> None:
        """好友戳一戳"""

    # ==================================================================
    # 音乐消息
    # ==================================================================

    @abstractmethod
    async def send_group_music(
        self,
        group_id: Union[str, int],
        type: Literal["qq", "163"],
        id: Union[int, str],
    ) -> Any:
        """发送群音乐分享"""

    @abstractmethod
    async def send_group_custom_music(
        self,
        group_id: Union[str, int],
        url: str,
        title: str,
        image: str,
        audio: Optional[str] = None,
        content: Optional[str] = None,
    ) -> Any:
        """发送群自定义音乐分享"""

    @abstractmethod
    async def send_private_music(
        self,
        user_id: Union[str, int],
        type: Literal["qq", "163"],
        id: Union[int, str],
    ) -> Any:
        """发送私聊音乐分享"""

    @abstractmethod
    async def send_private_custom_music(
        self,
        user_id: Union[str, int],
        url: str,
        title: str,
        image: str,
        audio: Optional[str] = None,
        content: Optional[str] = None,
    ) -> Any:
        """发送私聊自定义音乐分享"""
