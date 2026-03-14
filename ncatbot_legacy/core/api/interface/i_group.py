"""
IBotAPI 群管理接口

声明所有群管理相关的异步接口方法。
"""

from abc import ABC, abstractmethod
from typing import Any, List, Literal, Optional, Union


class IGroupAPI(ABC):
    """群管理操作接口

    包含：成员管理、群设置、文件管理、信息查询等。
    """

    # ==================================================================
    # 成员管理
    # ==================================================================

    @abstractmethod
    async def set_group_kick(
        self,
        group_id: Union[str, int],
        user_id: Union[str, int],
        reject_add_request: bool = False,
    ) -> None:
        """踢出群成员"""

    @abstractmethod
    async def set_group_ban(
        self,
        group_id: Union[str, int],
        user_id: Union[str, int],
        duration: int = 1800,
    ) -> None:
        """禁言群成员"""

    @abstractmethod
    async def set_group_whole_ban(
        self, group_id: Union[str, int], enable: bool = True
    ) -> None:
        """全群禁言"""

    @abstractmethod
    async def set_group_admin(
        self,
        group_id: Union[str, int],
        user_id: Union[str, int],
        enable: bool = True,
    ) -> None:
        """设置群管理员"""

    @abstractmethod
    async def set_group_card(
        self,
        group_id: Union[str, int],
        user_id: Union[str, int],
        card: str = "",
    ) -> None:
        """设置群名片"""

    @abstractmethod
    async def set_group_leave(
        self, group_id: Union[str, int], is_dismiss: bool = False
    ) -> None:
        """退出群组"""

    @abstractmethod
    async def set_group_special_title(
        self,
        group_id: Union[str, int],
        user_id: Union[str, int],
        special_title: str = "",
        duration: int = -1,
    ) -> None:
        """设置群成员专属头衔"""

    # ==================================================================
    # 群设置
    # ==================================================================

    @abstractmethod
    async def set_group_name(self, group_id: Union[str, int], name: str) -> None:
        """设置群名称"""

    @abstractmethod
    async def set_group_remark(self, group_id: Union[str, int], remark: str) -> None:
        """设置群备注"""

    @abstractmethod
    async def set_group_sign(self, group_id: Union[str, int]) -> None:
        """群签到"""

    @abstractmethod
    async def send_group_sign(self, group_id: Union[str, int]) -> None:
        """发送群签到"""

    @abstractmethod
    async def set_group_avatar(self, group_id: Union[str, int], file: str) -> None:
        """设置群头像"""

    @abstractmethod
    async def set_group_add_request(
        self,
        flag: str,
        sub_type: str,
        approve: bool = True,
        reason: str = "",
    ) -> None:
        """处理群请求/邀请"""

    # ==================================================================
    # 群相册
    # ==================================================================

    @abstractmethod
    async def get_group_album_list(self, group_id: Union[str, int]) -> List[dict]:
        """获取群相册列表"""

    @abstractmethod
    async def upload_image_to_group_album(
        self,
        group_id: Union[str, int],
        file: str,
        album_id: str = "",
        album_name: str = "",
    ) -> None:
        """上传图片到群相册"""

    # ==================================================================
    # 群公告与待办
    # ==================================================================

    @abstractmethod
    async def set_group_todo(
        self, group_id: Union[str, int], message_id: Union[str, int]
    ) -> dict:
        """设置群待办"""

    # ==================================================================
    # 精华消息
    # ==================================================================

    @abstractmethod
    async def set_essence_msg(self, message_id: Union[str, int]) -> None:
        """设置精华消息"""

    @abstractmethod
    async def delete_essence_msg(self, message_id: Union[str, int]) -> None:
        """删除精华消息"""

    @abstractmethod
    async def get_essence_msg_list(self, group_id: Union[str, int]) -> Any:
        """获取精华消息列表"""

    # ==================================================================
    # 群信息查询
    # ==================================================================

    @abstractmethod
    async def get_group_honor_info(
        self,
        group_id: Union[str, int],
        type: Literal["talkative", "performer", "legend", "emotion", "all"],
    ) -> Any:
        """获取群荣誉信息"""

    @abstractmethod
    async def get_group_info(self, group_id: Union[str, int]) -> Any:
        """获取群信息"""

    @abstractmethod
    async def get_group_info_ex(self, group_id: Union[str, int]) -> dict:
        """获取群扩展信息"""

    @abstractmethod
    async def get_group_list(self, info: bool = False) -> list:
        """获取群列表"""

    @abstractmethod
    async def get_group_member_info(
        self,
        group_id: Union[str, int],
        user_id: Union[str, int],
    ) -> Any:
        """获取群成员信息"""

    @abstractmethod
    async def get_group_member_list(self, group_id: Union[str, int]) -> Any:
        """获取群成员列表"""

    @abstractmethod
    async def get_group_shut_list(self, group_id: Union[str, int]) -> Any:
        """获取群禁言列表"""

    # ==================================================================
    # 群文件管理
    # ==================================================================

    @abstractmethod
    async def upload_group_file(
        self,
        group_id: Union[str, int],
        file: str,
        name: str,
        folder: Optional[str] = None,
    ) -> None:
        """上传群文件"""

    @abstractmethod
    async def move_group_file(
        self,
        group_id: Union[str, int],
        file_id: str,
        current_parent_directory: str,
        target_parent_directory: str,
    ) -> None:
        """移动群文件"""

    @abstractmethod
    async def trans_group_file(
        self, group_id: Union[str, int], file_id: str
    ) -> None:
        """转存群文件"""

    @abstractmethod
    async def rename_group_file(
        self,
        group_id: Union[str, int],
        file_id: str,
        new_name: str,
    ) -> None:
        """重命名群文件"""

    @abstractmethod
    async def get_file(self, file_id: str, file: str) -> Any:
        """获取文件信息"""

    @abstractmethod
    async def create_group_file_folder(
        self, group_id: Union[str, int], folder_name: str
    ) -> None:
        """创建群文件夹"""

    @abstractmethod
    async def delete_group_file(
        self, group_id: Union[str, int], file_id: str
    ) -> None:
        """删除群文件"""

    @abstractmethod
    async def delete_group_folder(
        self, group_id: Union[str, int], folder_id: str
    ) -> None:
        """删除群文件夹"""

    @abstractmethod
    async def get_group_root_files(
        self, group_id: Union[str, int], file_count: int = 50
    ) -> dict:
        """获取群根目录文件列表"""

    @abstractmethod
    async def get_group_files_by_folder(
        self,
        group_id: Union[str, int],
        folder_id: str,
        file_count: int = 50,
    ) -> dict:
        """获取群文件夹内文件列表"""

    @abstractmethod
    async def get_group_file_url(
        self, group_id: Union[str, int], file_id: str
    ) -> str:
        """获取群文件下载链接"""
