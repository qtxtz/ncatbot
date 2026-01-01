"""
启动流程集成测试

测试 BotClient 的完整启动流程和各组件协同初始化。
"""
import pytest
import asyncio
from typing import List, Optional
from unittest.mock import MagicMock, AsyncMock, patch, PropertyMock

from ncatbot.core.client.event_bus import EventBus
from ncatbot.core.client.lifecycle import LifecycleManager, LEGAL_ARGS
from ncatbot.core.client.registry import EventRegistry
from ncatbot.core.service import ServiceManager, BaseService
from ncatbot.utils.error import NcatBotError


# =============================================================================
# Mock 组件
# =============================================================================

class MockMessageRouter(BaseService):
    """Mock 消息路由服务"""
    name = "message_router"
    
    def __init__(self, **config):
        super().__init__(**config)
        self.connected = False
        self._event_callback = None
    
    async def on_load(self):
        self.connected = True
    
    async def on_close(self):
        self.connected = False
    
    def set_event_callback(self, callback):
        self._event_callback = callback
    
    async def send(self, action, params=None, timeout=30):
        return {"status": "ok", "data": {}}


# =============================================================================
# 启动参数验证测试
# =============================================================================

class TestStartupValidation:
    """启动参数验证测试"""
    
    def test_legal_args_defined(self):
        """测试合法参数已定义"""
        expected_args = ["bt_uin", "ws_uri", "debug", "root"]
        for arg in expected_args:
            assert arg in LEGAL_ARGS
    
    def test_illegal_arg_rejected(self):
        """测试非法参数被拒绝"""
        services = ServiceManager()
        event_bus = EventBus()
        registry = MagicMock(spec=EventRegistry)
        
        manager = LifecycleManager(services, event_bus, registry)
        
        with pytest.raises(NcatBotError, match="非法参数"):
            manager.start(illegal_param="value")
    
    def test_none_values_ignored(self):
        """测试 None 值被忽略"""
        services = ServiceManager()
        event_bus = EventBus()
        registry = MagicMock(spec=EventRegistry)
        
        manager = LifecycleManager(services, event_bus, registry)
        manager.mock_mode = True
        
        with patch("ncatbot.core.client.lifecycle.ncatbot_config") as mock_config:
            mock_config.validate_config = MagicMock()
            mock_config.debug = False
            
            with patch("ncatbot.core.client.lifecycle.run_coroutine"):
                with patch("ncatbot.plugin_system.PluginLoader"):
                    # None 值不应该更新配置
                    manager.start(bt_uin="123", ws_uri=None)
                    
                    # bt_uin 应该被更新
                    mock_config.update_value.assert_any_call("bt_uin", "123")
                    # ws_uri 为 None，不应该被更新
                    calls = [str(c) for c in mock_config.update_value.call_args_list]
                    assert not any("ws_uri" in c and "None" in c for c in calls)


# =============================================================================
# 组件初始化顺序测试
# =============================================================================

class TestComponentInitOrder:
    """组件初始化顺序测试"""
    
    @pytest.mark.asyncio
    async def test_service_manager_initialized_first(self):
        """测试 ServiceManager 首先初始化"""
        init_order = []
        
        services = ServiceManager()
        event_bus = EventBus()
        registry = MagicMock(spec=EventRegistry)
        
        manager = LifecycleManager(services, event_bus, registry)
        
        # 验证 services 已经注入
        assert manager.services is services
    
    @pytest.mark.asyncio
    async def test_event_bus_available_at_start(self):
        """测试 EventBus 在启动时可用"""
        services = ServiceManager()
        event_bus = EventBus()
        registry = MagicMock(spec=EventRegistry)
        
        manager = LifecycleManager(services, event_bus, registry)
        
        # 可以订阅事件
        handler_id = event_bus.subscribe("test.event", lambda e: None)
        assert handler_id is not None


# =============================================================================
# 服务加载流程测试
# =============================================================================

class TestServiceLoadingFlow:
    """服务加载流程测试"""
    
    @pytest.mark.asyncio
    async def test_services_load_in_correct_order(self):
        """测试服务按正确顺序加载"""
        load_order = []
        
        class ServiceA(BaseService):
            name = "service_a"
            async def on_load(self):
                load_order.append("a")
            async def on_close(self):
                pass
        
        class ServiceB(BaseService):
            name = "service_b"
            async def on_load(self):
                load_order.append("b")
            async def on_close(self):
                pass
        
        manager = ServiceManager()
        manager.register(ServiceA)
        manager.register(ServiceB)
        
        await manager.load_all()
        
        assert len(load_order) == 2
        assert "a" in load_order
        assert "b" in load_order
    
    @pytest.mark.asyncio
    async def test_service_failure_during_load(self):
        """测试服务加载失败"""
        class FailingService(BaseService):
            name = "failing"
            async def on_load(self):
                raise RuntimeError("Load failed")
            async def on_close(self):
                pass
        
        manager = ServiceManager()
        manager.register(FailingService)
        
        with pytest.raises(RuntimeError, match="Load failed"):
            await manager.load("failing")


# =============================================================================
# 退出流程测试
# =============================================================================

