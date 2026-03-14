"""
IBotAPI 抽象接口

定义与协议无关的 Bot 操作接口，由 Adapter 提供具体实现。
"""

from abc import ABC, abstractmethod
from typing import List, Union


class IBotAPI(ABC):
    """与协议无关的 Bot API 接口"""

    # ---- 消息操作 ----

    @abstractmethod
    async def send_private_msg(
        self, user_id: Union[str, int], message: list, **kwargs
    ) -> dict: ...

    @abstractmethod
    async def send_group_msg(
        self, group_id: Union[str, int], message: list, **kwargs
    ) -> dict: ...

    @abstractmethod
    async def delete_msg(self, message_id: Union[str, int]) -> None: ...

    @abstractmethod
    async def send_forward_msg(
        self,
        message_type: str,
        target_id: Union[str, int],
        messages: list,
        **kwargs,
    ) -> dict: ...

    # ---- 群管理 ----

    @abstractmethod
    async def set_group_kick(
        self, group_id: Union[str, int], user_id: Union[str, int],
        reject_add_request: bool = False,
    ) -> None: ...

    @abstractmethod
    async def set_group_ban(
        self, group_id: Union[str, int], user_id: Union[str, int],
        duration: int = 1800,
    ) -> None: ...

    @abstractmethod
    async def set_group_whole_ban(
        self, group_id: Union[str, int], enable: bool = True,
    ) -> None: ...

    @abstractmethod
    async def set_group_admin(
        self, group_id: Union[str, int], user_id: Union[str, int],
        enable: bool = True,
    ) -> None: ...

    @abstractmethod
    async def set_group_card(
        self, group_id: Union[str, int], user_id: Union[str, int],
        card: str = "",
    ) -> None: ...

    @abstractmethod
    async def set_group_name(
        self, group_id: Union[str, int], name: str,
    ) -> None: ...

    @abstractmethod
    async def set_group_leave(
        self, group_id: Union[str, int], is_dismiss: bool = False,
    ) -> None: ...

    @abstractmethod
    async def set_group_special_title(
        self, group_id: Union[str, int], user_id: Union[str, int],
        special_title: str = "",
    ) -> None: ...

    # ---- 账号操作 ----

    @abstractmethod
    async def set_friend_add_request(
        self, flag: str, approve: bool = True, remark: str = "",
    ) -> None: ...

    @abstractmethod
    async def set_group_add_request(
        self, flag: str, sub_type: str, approve: bool = True, reason: str = "",
    ) -> None: ...

    # ---- 信息查询 ----

    @abstractmethod
    async def get_login_info(self) -> dict: ...

    @abstractmethod
    async def get_stranger_info(self, user_id: Union[str, int]) -> dict: ...

    @abstractmethod
    async def get_friend_list(self) -> List[dict]: ...

    @abstractmethod
    async def get_group_info(self, group_id: Union[str, int]) -> dict: ...

    @abstractmethod
    async def get_group_list(self) -> list: ...

    @abstractmethod
    async def get_group_member_info(
        self, group_id: Union[str, int], user_id: Union[str, int],
    ) -> dict: ...

    @abstractmethod
    async def get_group_member_list(self, group_id: Union[str, int]) -> list: ...

    @abstractmethod
    async def get_msg(self, message_id: Union[str, int]) -> dict: ...

    @abstractmethod
    async def get_forward_msg(self, message_id: Union[str, int]) -> dict: ...

    # ---- 文件操作 ----

    @abstractmethod
    async def upload_group_file(
        self, group_id: Union[str, int], file: str, name: str, folder_id: str = "",
    ) -> None: ...

    @abstractmethod
    async def get_group_root_files(self, group_id: Union[str, int]) -> dict: ...

    @abstractmethod
    async def get_group_file_url(
        self, group_id: Union[str, int], file_id: str,
    ) -> str: ...

    @abstractmethod
    async def delete_group_file(
        self, group_id: Union[str, int], file_id: str,
    ) -> None: ...

    # ---- 辅助功能 ----

    @abstractmethod
    async def send_like(self, user_id: Union[str, int], times: int = 1) -> None: ...

    @abstractmethod
    async def send_poke(
        self, group_id: Union[str, int], user_id: Union[str, int],
    ) -> None: ...
