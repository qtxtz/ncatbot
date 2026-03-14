"""
NapCat API 实现

实现 IBotAPI 抽象接口，通过 NapCatProtocol 发送 OneBot v11 API 调用。
按职责拆分为多个 Mixin 模块：
  - _base: 协议调用与预上传工具方法
  - _message: 消息收发与转发
  - _group: 群管理操作
  - _account: 账号/好友/请求操作
  - _query: 信息查询
  - _file: 文件操作
  - _system: AI/系统/辅助功能
"""

from __future__ import annotations

from typing import Optional

from ncatbot.core.api.interface import IBotAPI

from ..preupload import PreUploadService
from ..protocol import NapCatProtocol
from ._account import AccountMixin
from ._file import FileMixin
from ._group import GroupMixin
from ._message import MessageMixin
from ._query import QueryMixin
from ._system import SystemMixin


class NapCatBotAPI(
    MessageMixin,
    GroupMixin,
    AccountMixin,
    QueryMixin,
    FileMixin,
    SystemMixin,
    IBotAPI,
):
    """NapCat 平台的 IBotAPI 实现

    将标准 IBotAPI 调用转换为 OneBot v11 协议请求，
    通过 NapCatProtocol 发送并返回结果。
    """

    def __init__(self, protocol: NapCatProtocol, preupload: Optional[PreUploadService] = None):
        super().__init__(protocol, preupload)


__all__ = ["NapCatBotAPI"]
