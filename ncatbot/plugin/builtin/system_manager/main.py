"""
系统管理插件

内置插件，负责：
- 插件配置管理（查看/修改任意插件配置）
- 心跳超时检测（meta 事件监控）
"""

import asyncio
import time as time_mod
from typing import Any, Dict, Optional

from ...ncatbot_plugin import NcatBotPlugin
from ncatbot.utils import get_log

LOG = get_log("SystemManager")


class SystemManagerPlugin(NcatBotPlugin):
    """系统管理插件"""

    name = "_system_manager"
    version = "1.0.0"
    author = "NcatBot"
    description = "系统内置管理插件：插件配置管理、心跳超时检测"

    def _init_(self) -> None:
        self._last_heartbeat_time: float = time_mod.time()
        self._heartbeat_monitor_task: Optional[asyncio.Task] = None

    async def on_load(self) -> None:
        # 启动心跳监听
        self._heartbeat_monitor_task = asyncio.create_task(
            self._heartbeat_monitor_loop()
        )

        # 启动定时心跳超时检查（每 30s）
        self.add_scheduled_task("_check_heartbeat_timeout", "30s")

        LOG.info("系统管理插件已加载")

    async def on_close(self) -> None:
        if self._heartbeat_monitor_task and not self._heartbeat_monitor_task.done():
            self._heartbeat_monitor_task.cancel()
            try:
                await self._heartbeat_monitor_task
            except asyncio.CancelledError:
                pass

        LOG.info("系统管理插件已关闭")

    # ------------------------------------------------------------------
    # 功能 A: 插件配置管理
    # ------------------------------------------------------------------

    def get_plugin_config(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """获取指定插件的配置字典。"""
        plugin = self.get_plugin(plugin_name)
        if plugin is None:
            return None
        return getattr(plugin, "config", None)

    def set_plugin_config(self, plugin_name: str, key: str, value: Any) -> bool:
        """设置指定插件的配置项并持久化。"""
        plugin = self.get_plugin(plugin_name)
        if plugin is None:
            return False
        set_config = getattr(plugin, "set_config", None)
        if callable(set_config):
            set_config(key, value)
            return True
        config = getattr(plugin, "config", None)
        if isinstance(config, dict):
            config[key] = value
            return True
        return False

    def list_plugin_configs(self) -> Dict[str, Dict[str, Any]]:
        """列出所有已加载插件的配置。"""
        result = {}
        for name in self.list_plugins():
            plugin = self.get_plugin(name)
            if plugin is not None:
                result[name] = getattr(plugin, "config", {})
        return result

    # ------------------------------------------------------------------
    # 功能 B: 心跳超时检测
    # ------------------------------------------------------------------

    async def _heartbeat_monitor_loop(self) -> None:
        """监听心跳事件，更新最后心跳时间。"""
        try:
            async with self.events("meta_event.heartbeat") as stream:
                async for event in stream:
                    self._last_heartbeat_time = time_mod.time()
        except asyncio.CancelledError:
            pass

    async def _check_heartbeat_timeout(self) -> None:
        """定时任务：检查心跳是否超时。"""
        timeout = self.get_config("heartbeat_timeout", 60)
        elapsed = time_mod.time() - self._last_heartbeat_time

        if elapsed > timeout:
            LOG.warning(
                "心跳超时: 已 %.1f 秒未收到心跳 (阈值: %ds)",
                elapsed,
                timeout,
            )
            await self._emit_heartbeat_timeout(elapsed, timeout)

    async def _emit_heartbeat_timeout(self, elapsed: float, timeout: int) -> None:
        """发出心跳超时事件。"""
        from ncatbot.types.qq import HeartbeatTimeoutMetaEventData

        event_data = HeartbeatTimeoutMetaEventData(
            time=int(time_mod.time()),
            self_id="0",
            last_heartbeat_time=int(self._last_heartbeat_time),
            timeout_seconds=timeout,
        )
        await self._dispatcher.callback(event_data)
