"""
IBotAPI 账号接口

声明所有账号管理相关的异步接口方法。
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Literal, Optional, Union


class IAccountAPI(ABC):
    """账号管理操作接口

    包含：账号设置、好友管理、消息状态等。
    """

    # ==================================================================
    # 账号设置
    # ==================================================================

    @abstractmethod
    async def set_qq_profile(
        self,
        nickname: str,
        personal_note: str,
        sex: Literal["未知", "男", "女"],
    ) -> None:
        """设置 QQ 资料"""

    @abstractmethod
    async def set_online_status(
        self,
        status: int,
        ext_status: int,
        battery_status: int,
    ) -> None:
        """设置在线状态"""

    @abstractmethod
    async def set_qq_avatar(self, file: str) -> None:
        """设置 QQ 头像"""

    @abstractmethod
    async def set_self_longnick(self, long_nick: str) -> None:
        """设置个人长昵称"""

    # ==================================================================
    # 账号信息查询
    # ==================================================================

    @abstractmethod
    async def get_login_info(self) -> Any:
        """获取当前登录账号信息"""

    @abstractmethod
    async def get_status(self) -> dict:
        """获取当前状态"""

    # ==================================================================
    # 好友管理
    # ==================================================================

    @abstractmethod
    async def get_friends_with_cat(self) -> List[dict]:
        """获取好友列表（带分类）"""

    @abstractmethod
    async def send_like(
        self,
        user_id: Union[str, int],
        times: int = 1,
    ) -> Any:
        """给好友点赞"""

    @abstractmethod
    async def set_friend_add_request(
        self,
        flag: str,
        approve: bool,
        remark: Optional[str] = None,
    ) -> None:
        """处理好友添加请求"""

    @abstractmethod
    async def get_friend_list(self) -> List[dict]:
        """获取好友列表"""

    @abstractmethod
    async def delete_friend(
        self,
        user_id: Union[str, int],
        block: bool = True,
        both: bool = True,
    ) -> None:
        """删除好友"""

    @abstractmethod
    async def set_friend_remark(
        self,
        user_id: Union[str, int],
        remark: str,
    ) -> None:
        """设置好友备注"""

    @abstractmethod
    async def get_stranger_info(self, user_id: Union[str, int]) -> Any:
        """获取陌生人信息"""

    # ==================================================================
    # 消息状态
    # ==================================================================

    @abstractmethod
    async def mark_group_msg_as_read(self, group_id: Union[str, int]) -> None:
        """将群消息标记为已读"""

    @abstractmethod
    async def mark_private_msg_as_read(self, user_id: Union[str, int]) -> None:
        """将私聊消息标记为已读"""

    @abstractmethod
    async def create_collection(self, raw_data: str, brief: str) -> None:
        """创建收藏"""

    @abstractmethod
    async def get_recent_contact(self) -> List[dict]:
        """获取最近联系人"""

    # ==================================================================
    # 其它
    # ==================================================================

    @abstractmethod
    async def ask_share_group(self, group_id: Union[str, int]) -> None:
        """请求分享群"""

    @abstractmethod
    async def fetch_custom_face(self, count: int = 48) -> Any:
        """获取自定义表情"""

    @abstractmethod
    async def nc_get_user_status(self, user_id: Union[str, int]) -> dict:
        """获取用户状态"""
