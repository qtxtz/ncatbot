"""
IBotAPI 抽象接口

定义与协议无关的 Bot 操作接口，由 Adapter 提供具体实现。
位于 Layer 2（Abstract API），Core 层和 Plugin 层通过此接口调用 API。

接口按功能分组在以下文件中声明：
- i_message.py: 消息操作（发送/撤回/转发/获取/戳一戳/音乐）
- i_group.py: 群管理（成员/设置/文件/信息查询）
- i_account.py: 账号管理（资料/好友/消息状态）
- i_private.py: 私聊操作（文件/输入状态）
- i_support.py: 辅助功能（AI/OCR/系统）
"""

from .i_message import IMessageAPI
from .i_group import IGroupAPI
from .i_account import IAccountAPI
from .i_private import IPrivateAPI
from .i_support import ISupportAPI


class IBotAPI(IMessageAPI, IGroupAPI, IAccountAPI, IPrivateAPI, ISupportAPI):
    """与协议无关的 Bot API 完整接口

    此接口定义框架期望的所有 Bot 操作。
    各 Adapter 提供具体实现。

    接口分类：
    1. 消息操作：发送、撤回、转发、获取、戳一戳、音乐
    2. 群管理：成员管理、群设置、文件管理、信息查询
    3. 账号操作：设置资料、好友管理、消息状态
    4. 私聊操作：文件上传下载、输入状态
    5. 辅助功能：AI 声聊、OCR、版本信息
    """


__all__ = [
    "IBotAPI",
    "IMessageAPI",
    "IGroupAPI",
    "IAccountAPI",
    "IPrivateAPI",
    "ISupportAPI",
]
