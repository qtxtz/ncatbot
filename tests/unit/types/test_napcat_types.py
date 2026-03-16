"""
NapCat 响应类型模型规范测试

规范:
  N-01: NapCatModel 自动将 int 类型 *_id 字段转为 str
  N-02: NapCatModel 支持字典兼容访问 (__getitem__, get, __contains__)
  N-03: NapCatModel 允许额外字段 (extra="allow")
  N-04: SendMessageResult 正确解析 message_id
  N-05: 各模型基本构造不报错
"""

import pytest

from ncatbot.types.napcat import (
    NapCatModel,
    SendMessageResult,
    MessageData,
    MessageHistory,
    ForwardMessageData,
    GroupInfo,
    GroupMemberInfo,
    GroupNotice,
    EssenceMessage,
    GroupHonorInfo,
    GroupAtAllRemain,
    GroupShutInfo,
    GroupSystemMsg,
    GroupInfoEx,
    LoginInfo,
    StrangerInfo,
    FriendInfo,
    GroupFileSystemInfo,
    GroupFileList,
    FileData,
    DownloadResult,
    VersionInfo,
    BotStatus,
    EmojiLikeInfo,
    OcrResult,
)


# ---- N-01: ID 强转 ----


class _IdModel(NapCatModel):
    user_id: str = ""
    group_id: str = ""


def test_napcat_model_coerces_int_id_to_str():
    """N-01: NapCatModel 将 int 类型 *_id 字段自动转为 str"""
    m = _IdModel.model_validate({"user_id": 12345, "group_id": 67890})
    assert m.user_id == "12345"
    assert m.group_id == "67890"


def test_napcat_model_keeps_str_id():
    """N-01: 已经是 str 的 *_id 不受影响"""
    m = _IdModel.model_validate({"user_id": "abc", "group_id": "def"})
    assert m.user_id == "abc"
    assert m.group_id == "def"


# ---- N-02: 字典兼容 ----


def test_napcat_model_getitem():
    """N-02: NapCatModel 支持 model['key'] 访问"""
    m = SendMessageResult(message_id="42")
    assert m["message_id"] == "42"


def test_napcat_model_get_with_default():
    """N-02: NapCatModel 支持 model.get('key', default) 访问"""
    m = SendMessageResult(message_id="42")
    assert m.get("message_id") == "42"
    assert m.get("nonexistent", "fallback") == "fallback"


def test_napcat_model_contains():
    """N-02: NapCatModel 支持 'key' in model"""
    m = SendMessageResult(message_id="42")
    assert "message_id" in m
    assert "nonexistent" not in m


# ---- N-03: 额外字段 ----


def test_napcat_model_extra_fields():
    """N-03: NapCatModel 允许额外字段"""
    m = SendMessageResult.model_validate({"message_id": "1", "extra_field": "value"})
    assert m.message_id == "1"
    assert m.extra_field == "value"


# ---- N-04: SendMessageResult ----


def test_send_message_result():
    """N-04: SendMessageResult 解析 message_id"""
    r = SendMessageResult(message_id="123")
    assert r.message_id == "123"


def test_send_message_result_int_coerce():
    """N-04: SendMessageResult 将 int message_id 转为 str"""
    r = SendMessageResult.model_validate({"message_id": 123})
    assert r.message_id == "123"


# ---- N-05: 各模型基本构造 ----


@pytest.mark.parametrize(
    "model_cls, data",
    [
        (SendMessageResult, {"message_id": "1"}),
        (MessageData, {"message_id": "1"}),
        (MessageHistory, {}),
        (ForwardMessageData, {}),
        (GroupInfo, {"group_id": "123"}),
        (GroupMemberInfo, {"group_id": "1", "user_id": "2"}),
        (GroupNotice, {}),
        (EssenceMessage, {}),
        (GroupHonorInfo, {}),
        (GroupAtAllRemain, {}),
        (GroupShutInfo, {}),
        (GroupSystemMsg, {}),
        (GroupInfoEx, {}),
        (LoginInfo, {"user_id": "1"}),
        (StrangerInfo, {"user_id": "1"}),
        (FriendInfo, {"user_id": "1"}),
        (GroupFileSystemInfo, {}),
        (GroupFileList, {}),
        (FileData, {}),
        (DownloadResult, {"file": "/tmp/a.txt"}),
        (VersionInfo, {}),
        (BotStatus, {}),
        (EmojiLikeInfo, {}),
        (OcrResult, {}),
    ],
)
def test_model_construction(model_cls, data):
    """N-05: 各模型可以从最小数据构造"""
    m = model_cls.model_validate(data)
    assert m is not None
