"""统一注册服务

负责命令和过滤器的统一管理功能。
"""

import asyncio
import traceback
from typing import Dict, Callable, TYPE_CHECKING, List, Tuple, Optional

from ncatbot.utils import get_log
from ...base import BaseService
from .trigger.binder import BindResult
from .trigger.preprocessor import MessagePreprocessor, PreprocessResult
from .command_system.lexer.tokenizer import StringTokenizer, Token
from .trigger.resolver import CommandResolver
from .trigger.binder import ArgumentBinder
from .filter_system import filter_registry
from .filter_system.validator import FilterValidator
from .command_system.registry.registry import command_registry
from .command_system.utils import CommandSpec
from .legacy_registry import legacy_registry

if TYPE_CHECKING:
    from ncatbot.core import MessageEvent, BaseEvent, NcatBotEvent

LOG = get_log("UnifiedRegistryService")


class UnifiedRegistryService(BaseService):
    """统一注册服务

    提供过滤器和命令的统一管理功能。
    """

    name = "unified_registry"
    description = "统一的过滤器和命令注册服务"

    def __init__(self, **config):
        super().__init__(**config)
        self._filter_validator: Optional[FilterValidator] = None
        self._func_plugin_map: Dict[Callable, object] = {}
        self.filter_registry = filter_registry
        self.command_registry = command_registry
        self._binder: Optional[ArgumentBinder] = None
        self._initialized = False
        self._preprocessor: Optional[MessagePreprocessor] = None
        self._resolver: Optional[CommandResolver] = None
        self.prefixes: List[str] = []

    async def on_load(self) -> None:
        """服务加载时的初始化"""
        self._filter_validator = FilterValidator()
        self._binder = ArgumentBinder()
        LOG.info("统一注册服务已加载")

    async def on_close(self) -> None:
        """服务关闭时清理"""
        self.clear()
        LOG.info("统一注册服务已关闭")

    # ------------------------------------------------------------------
    # 便捷属性
    # ------------------------------------------------------------------

    @property
    def plugins(self) -> List:
        """获取已加载的插件列表"""
        if self.plugin_loader:
            return list(self.plugin_loader.plugins.values())
        return []

    def _normalize_case(self, s: str) -> str:
        """大小写归一化"""
        # TODO: 实现大小写敏感（可能永远不会做）
        return s

    def _find_plugin_for_function(self, func: Callable):
        """查找函数所属的插件"""
        if func in self._func_plugin_map:
            return self._func_plugin_map[func]

        for plugin in self.plugins:
            plugin_class = plugin.__class__
            if func in plugin_class.__dict__.values():
                self._func_plugin_map[func] = plugin
                return plugin

        return None

    def handle_plugin_unload(self, plugin_name: str) -> None:
        """处理插件卸载，清理相关缓存"""
        LOG.debug(f"处理插件卸载: {plugin_name}")
        self._initialized = False
        self.command_registry.root_group.revoke_plugin(plugin_name)
        self.filter_registry.revoke_plugin(plugin_name)
        self.initialize_if_needed()

    def handle_plugin_load(self) -> None:
        """处理插件加载，重新初始化"""
        self._initialized = False
        self.initialize_if_needed()

    async def _execute_function(
        self,
        func: Callable,
        event: "MessageEvent",
        *args,
        **kwargs
    ):
        """执行函数"""
        plugin = self._find_plugin_for_function(func)

        try:
            # 使用过滤器验证器
            if hasattr(func, "__filters__"):
                if not self._filter_validator.validate_filters(func, event):
                    return False
            call_args = (plugin, event) + args if plugin else (event,) + args
            if asyncio.iscoroutinefunction(func):
                return await func(*call_args, **kwargs)
            else:
                return await asyncio.to_thread(func, *call_args, **kwargs)
        except Exception as e:
            LOG.error(f"执行函数 {func.__name__} 时发生错误: {e}")
            LOG.info(f"{traceback.format_exc()}")
            return False

    async def run_pure_filters(self, event: "MessageEvent") -> None:
        """遍历执行纯过滤器函数（不含命令函数）"""
        for func in filter_registry._function_filters.values():
            if getattr(func, "__is_command__", False):
                continue
            await self._execute_function(func, event)

    async def run_command(self, event: "MessageEvent") -> bool:
        """运行命令处理"""
        # 前置检查与提取首段文本
        pre: Optional[PreprocessResult] = self._preprocessor.precheck(event)
        if pre is None:
            return False

        text = pre.command_text
        first_word = text.split(" ")[0]

        commands = self._resolver.get_commands()
        hit = [
            command
            for command in commands
            if first_word.endswith(command.path_words[0])
        ]
        if not hit:
            return False

        tokenizer = StringTokenizer(text)
        tokens: List[Token] = tokenizer.tokenize()

        prefix, match = self._resolver.resolve_from_tokens(tokens)
        if match is None:
            return False
        if prefix not in match.command.prefixes:
            return False

        LOG.debug(f"命中命令: {match.command.func.__name__}")

        func = match.command.func
        ignore_words = match.path_words
        try:
            bind_result: BindResult = self._binder.bind(
                match.command, event, ignore_words, [prefix]
            )
        except Exception as e:
            from ncatbot.core.client import NcatBotEvent
            await self.event_bus.publish(
                NcatBotEvent(
                    type="ncatbot.param_bind_failed",
                    data={"event": event, "msg": str(e), "cmd": match.command.name},
                )
            )
            return False

        try:
            await self._execute_function(
                func, event, *bind_result.args,
                **bind_result.named_args
            )
        except Exception:
            traceback.print_exc()

        return True

    async def handle_message_event(self, event: "MessageEvent") -> None:
        """处理消息事件（命令和过滤器）"""
        self.initialize_if_needed()
        await self.run_command(event)
        await self.run_pure_filters(event)

    def initialize_if_needed(self) -> None:
        """首次触发时构建命令分发表并做严格冲突检测"""
        if self._initialized:
            return

        self._initialized = True

        self.prefixes = list(
            dict.fromkeys(
                prefix
                for registry in command_registry.command_registries
                for prefix in registry.prefixes
            )
        )
        if "" in self.prefixes:
            self.prefixes.remove("")
        LOG.info(f"命令前缀集合: {self.prefixes}")

        self._preprocessor = MessagePreprocessor(
            prefixes=self.prefixes,
            require_prefix=False,
            case_sensitive=False,
        )

        self._resolver = CommandResolver(
            allow_hierarchical=False,
            prefixes=self.prefixes,
            case_sensitive=False,
        )

        # 检查消息级前缀集合冲突
        norm_prefixes = [self._normalize_case(p) for p in self._preprocessor.prefixes]
        for i, p1 in enumerate(norm_prefixes):
            for j, p2 in enumerate(norm_prefixes):
                if i == j:
                    continue
                if p2.startswith(p1):
                    LOG.error(f"消息前缀冲突: '{p1}' 与 '{p2}' 存在包含关系")
                    raise ValueError(f"prefix conflict: {p1} vs {p2}")

        command_map = command_registry.get_all_commands()
        alias_map = command_registry.get_all_aliases()

        filtered_commands: Dict[Tuple[str, ...], CommandSpec] = {}
        for path, command in command_map.items():
            if getattr(command.func, "__is_command__", False):
                filtered_commands[path] = command

        filtered_aliases: Dict[Tuple[str, ...], CommandSpec] = {}
        for path, command in alias_map.items():
            if getattr(command.func, "__is_command__", False):
                filtered_aliases[path] = command

        self._resolver.build_index(filtered_commands, filtered_aliases)
        LOG.debug(
            f"TriggerEngine 初始化完成：命令={len(filtered_commands)}, 别名={len(filtered_aliases)}"
        )

    async def handle_legacy_event(self, event_data: "BaseEvent") -> bool:
        """处理通知和请求事件"""
        if event_data.post_type == "notice":
            for func in legacy_registry._notice_event:
                await self._execute_function(func, event_data)
        elif event_data.post_type == "request":
            for func in legacy_registry._request_event:
                await self._execute_function(func, event_data)
        return True

    def clear(self):
        """清理缓存"""
        self._func_plugin_map.clear()
        self._initialized = False
        if self._resolver:
            self._resolver.clear()

