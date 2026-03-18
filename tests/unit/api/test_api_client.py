"""
BotAPIClient 规范测试

规范:
  A-01: QQ API 命名空间可通过 api.qq 访问
  A-02: messaging 命名空间包含消息操作
  A-03: manage 命名空间包含群管操作
  A-04: query 命名空间包含查询操作
  A-05: __getattr__ 兜底透传未定义平台
"""

import pytest

from ncatbot.adapter.mock.api import MockBotAPI
from ncatbot.api.client import BotAPIClient
from ncatbot.api.qq import QQAPIClient

pytestmark = pytest.mark.asyncio


@pytest.fixture
def client():
    mock = MockBotAPI()
    api = BotAPIClient()
    api.register_platform("qq", QQAPIClient(mock))
    return api, mock


# ---- A-01: QQ 平台访问 ----


def test_qq_platform_accessible(client):
    """A-01: api.qq 返回 QQAPIClient 实例"""
    api, _ = client
    assert isinstance(api.qq, QQAPIClient)


# ---- A-02: messaging 命名空间 ----


async def test_send_group_msg(client):
    """A-02: api.qq.messaging.send_group_msg() 可直接调用"""
    api, mock = client
    mock.set_response("send_group_msg", {"message_id": "1"})
    result = await api.qq.messaging.send_group_msg("12345", [])
    assert result == {"message_id": "1"}
    assert mock.called("send_group_msg")


async def test_send_private_msg(client):
    """A-02: api.qq.messaging.send_private_msg() 可直接调用"""
    api, mock = client
    await api.qq.messaging.send_private_msg("99999", [])
    assert mock.called("send_private_msg")


async def test_delete_msg(client):
    """A-02: api.qq.messaging.delete_msg() 可直接调用"""
    api, mock = client
    await api.qq.messaging.delete_msg("1001")
    assert mock.called("delete_msg")


# ---- A-03: manage 命名空间 ----


def test_manage_namespace_exists(client):
    """A-03: api.qq.manage 属性存在"""
    api, _ = client
    assert hasattr(api.qq, "manage")


# ---- A-04: query 命名空间 ----


def test_query_namespace_exists(client):
    """A-04: api.qq.query 属性存在"""
    api, _ = client
    assert hasattr(api.qq, "query")


# ---- A-05: 未注册平台 ----


def test_unregistered_platform_raises(client):
    """A-05: 访问未注册的平台抛出 KeyError"""
    api, _ = client
    with pytest.raises(KeyError):
        api.platform("telegram")
