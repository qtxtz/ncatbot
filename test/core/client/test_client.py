"""
BotClient 集成测试
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from ncatbot.utils.error import NcatBotError


@pytest.fixture(autouse=True)
def reset_bot_client_singleton():
    """每个测试前重置 BotClient 单例状态"""
    from ncatbot.core.client.client import BotClient
    BotClient._initialized = False
    yield
    BotClient._initialized = False


class TestBotClientSingleton:
    """测试 BotClient 单例"""

    def test_client_singleton_first_instance(self):
        """第一次实例化成功"""
        with patch("ncatbot.core.client.client.Adapter") as mock_adapter_class:
            with patch("ncatbot.core.client.client.BotAPI") as mock_api_class:
                mock_adapter = MagicMock()
                mock_adapter.send = AsyncMock()
                mock_adapter_class.return_value = mock_adapter
                
                mock_api = MagicMock()
                mock_api_class.return_value = mock_api
                
                from ncatbot.core.client.client import BotClient
                
                client = BotClient()
                
                assert client is not None
                assert BotClient._initialized is True

    def test_client_singleton_second_instance_raises(self):
        """第二次实例化抛出异常"""
        with patch("ncatbot.core.client.client.Adapter") as mock_adapter_class:
            with patch("ncatbot.core.client.client.BotAPI") as mock_api_class:
                mock_adapter = MagicMock()
                mock_adapter.send = AsyncMock()
                mock_adapter_class.return_value = mock_adapter
                
                mock_api = MagicMock()
                mock_api_class.return_value = mock_api
                
                from ncatbot.core.client.client import BotClient
                
                client1 = BotClient()
                
                with pytest.raises(NcatBotError, match="BotClient 实例只能创建一次"):
                    client2 = BotClient()


class TestBotClientComponents:
    """测试 BotClient 组件初始化"""

    def test_client_components_initialized(self):
        """所有组件正确初始化"""
        with patch("ncatbot.core.client.client.Adapter") as mock_adapter_class:
            with patch("ncatbot.core.client.client.BotAPI") as mock_api_class:
                mock_adapter = MagicMock()
                mock_adapter.send = AsyncMock()
                mock_adapter_class.return_value = mock_adapter
                
                mock_api = MagicMock()
                mock_api_class.return_value = mock_api
                
                from ncatbot.core.client.client import BotClient
                
                client = BotClient()
                
                assert client.event_bus is not None
                assert client.adapter is mock_adapter
                assert client.api is mock_api
                assert client.dispatcher is not None

    def test_client_event_bus_type(self):
        """EventBus 类型正确"""
        with patch("ncatbot.core.client.client.Adapter") as mock_adapter_class:
            with patch("ncatbot.core.client.client.BotAPI") as mock_api_class:
                mock_adapter = MagicMock()
                mock_adapter.send = AsyncMock()
                mock_adapter_class.return_value = mock_adapter
                
                mock_api = MagicMock()
                mock_api_class.return_value = mock_api
                
                from ncatbot.core.client.client import BotClient
                from ncatbot.core.client.event_bus import EventBus
                
                client = BotClient()
                
                assert isinstance(client.event_bus, EventBus)

    def test_client_dispatcher_type(self):
        """EventDispatcher 类型正确"""
        with patch("ncatbot.core.client.client.Adapter") as mock_adapter_class:
            with patch("ncatbot.core.client.client.BotAPI") as mock_api_class:
                mock_adapter = MagicMock()
                mock_adapter.send = AsyncMock()
                mock_adapter_class.return_value = mock_adapter
                
                mock_api = MagicMock()
                mock_api_class.return_value = mock_api
                
                from ncatbot.core.client.client import BotClient
                from ncatbot.core.client.dispatcher import EventDispatcher
                
                client = BotClient()
                
                assert isinstance(client.dispatcher, EventDispatcher)


class TestBotClientInheritance:
    """测试 BotClient 继承"""

    def test_client_inherits_registry(self):
        """继承 EventRegistry 的所有方法"""
        with patch("ncatbot.core.client.client.Adapter") as mock_adapter_class:
            with patch("ncatbot.core.client.client.BotAPI") as mock_api_class:
                mock_adapter = MagicMock()
                mock_adapter.send = AsyncMock()
                mock_adapter_class.return_value = mock_adapter
                
                mock_api = MagicMock()
                mock_api_class.return_value = mock_api
                
                from ncatbot.core.client.client import BotClient
                from ncatbot.core.client.registry import EventRegistry
                
                client = BotClient()
                
                assert isinstance(client, EventRegistry)
                assert hasattr(client, "on_group_message")
                assert hasattr(client, "on_private_message")
                assert hasattr(client, "on_notice")
                assert hasattr(client, "on_startup")
                assert hasattr(client, "subscribe")
                assert hasattr(client, "register_handler")

    def test_client_decorators_work(self):
        """装饰器方法正常工作"""
        with patch("ncatbot.core.client.client.Adapter") as mock_adapter_class:
            with patch("ncatbot.core.client.client.BotAPI") as mock_api_class:
                mock_adapter = MagicMock()
                mock_adapter.send = AsyncMock()
                mock_adapter_class.return_value = mock_adapter
                
                mock_api = MagicMock()
                mock_api_class.return_value = mock_api
                
                from ncatbot.core.client.client import BotClient
                
                client = BotClient()
                
                @client.on_group_message()
                async def handler(event):
                    pass
                
                assert "message_event" in client.event_bus._exact


class TestBotClientPluginManagement:
    """测试 BotClient 插件管理"""

    def test_get_registered_plugins_empty(self):
        """无插件时返回空列表"""
        with patch("ncatbot.core.client.client.Adapter") as mock_adapter_class:
            with patch("ncatbot.core.client.client.BotAPI") as mock_api_class:
                mock_adapter = MagicMock()
                mock_adapter.send = AsyncMock()
                mock_adapter_class.return_value = mock_adapter
                
                mock_api = MagicMock()
                mock_api_class.return_value = mock_api
                
                from ncatbot.core.client.client import BotClient
                
                client = BotClient()
                client._lifecycle.plugin_loader = None
                
                result = client.get_registered_plugins()
                
                assert result == []

    def test_get_registered_plugins_with_loader(self):
        """有插件加载器时返回插件列表"""
        with patch("ncatbot.core.client.client.Adapter") as mock_adapter_class:
            with patch("ncatbot.core.client.client.BotAPI") as mock_api_class:
                mock_adapter = MagicMock()
                mock_adapter.send = AsyncMock()
                mock_adapter_class.return_value = mock_adapter
                
                mock_api = MagicMock()
                mock_api_class.return_value = mock_api
                
                from ncatbot.core.client.client import BotClient
                
                client = BotClient()
                
                mock_plugin1 = MagicMock()
                mock_plugin2 = MagicMock()
                mock_loader = MagicMock()
                mock_loader.plugins = {"plugin1": mock_plugin1, "plugin2": mock_plugin2}
                client._lifecycle.plugin_loader = mock_loader
                
                result = client.get_registered_plugins()
                
                assert len(result) == 2
                assert mock_plugin1 in result
                assert mock_plugin2 in result

    def test_get_plugin_by_type_found(self):
        """按类型获取插件 - 找到"""
        with patch("ncatbot.core.client.client.Adapter") as mock_adapter_class:
            with patch("ncatbot.core.client.client.BotAPI") as mock_api_class:
                mock_adapter = MagicMock()
                mock_adapter.send = AsyncMock()
                mock_adapter_class.return_value = mock_adapter
                
                mock_api = MagicMock()
                mock_api_class.return_value = mock_api
                
                from ncatbot.core.client.client import BotClient
                
                client = BotClient()
                
                class TestPluginType:
                    pass
                
                mock_plugin = TestPluginType()
                mock_loader = MagicMock()
                mock_loader.plugins = {"test": mock_plugin}
                client._lifecycle.plugin_loader = mock_loader
                
                result = client.get_plugin(TestPluginType)
                
                assert result is mock_plugin

    def test_get_plugin_by_type_not_found(self):
        """按类型获取插件 - 未找到抛出异常"""
        with patch("ncatbot.core.client.client.Adapter") as mock_adapter_class:
            with patch("ncatbot.core.client.client.BotAPI") as mock_api_class:
                mock_adapter = MagicMock()
                mock_adapter.send = AsyncMock()
                mock_adapter_class.return_value = mock_adapter
                
                mock_api = MagicMock()
                mock_api_class.return_value = mock_api
                
                from ncatbot.core.client.client import BotClient
                
                client = BotClient()
                
                class TestPluginType:
                    pass
                
                class OtherPluginType:
                    pass
                
                mock_plugin = OtherPluginType()
                mock_loader = MagicMock()
                mock_loader.plugins = {"other": mock_plugin}
                client._lifecycle.plugin_loader = mock_loader
                
                with pytest.raises(ValueError, match="未找到"):
                    client.get_plugin(TestPluginType)


class TestBotClientAdapterSetup:
    """测试 Adapter 设置"""

    def test_adapter_callback_set(self):
        """Adapter 回调设置正确"""
        with patch("ncatbot.core.client.client.Adapter") as mock_adapter_class:
            with patch("ncatbot.core.client.client.BotAPI") as mock_api_class:
                mock_adapter = MagicMock()
                mock_adapter.send = AsyncMock()
                mock_adapter_class.return_value = mock_adapter
                
                mock_api = MagicMock()
                mock_api_class.return_value = mock_api
                
                from ncatbot.core.client.client import BotClient
                
                client = BotClient()
                
                mock_adapter.set_event_callback.assert_called_once_with(client.dispatcher)


class TestBotClientBuiltinHandlers:
    """测试内置处理器"""

    def test_builtin_startup_handler_registered(self):
        """内置启动处理器注册"""
        with patch("ncatbot.core.client.client.Adapter") as mock_adapter_class:
            with patch("ncatbot.core.client.client.BotAPI") as mock_api_class:
                mock_adapter = MagicMock()
                mock_adapter.send = AsyncMock()
                mock_adapter_class.return_value = mock_adapter
                
                mock_api = MagicMock()
                mock_api_class.return_value = mock_api
                
                from ncatbot.core.client.client import BotClient
                
                client = BotClient()
                
                assert "meta_event" in client.event_bus._exact
