import asyncio
import threading
import uuid
from typing import Dict, Optional, Callable, Awaitable

from ..base import BaseService
from ncatbot.core.adapter.nc import NapCatWebSocket
from ncatbot.utils import get_log, ncatbot_config

LOG = get_log("MessageRouter")


class MessageRouter(BaseService):
    """
    消息路由服务 (线程安全版)

    改进点：
    1. 使用 threading.Lock 保护 _pending_futures 字典的并发访问
    2. 使用 asyncio.Future 实现高效的请求-响应匹配
    3. 通过 call_soon_threadsafe 确保跨线程操作 Future 的安全性
    """

    name = "message_router"
    description = "消息路由服务"
    _loop: asyncio.AbstractEventLoop

    def __init__(
        self,
        uri: Optional[str] = None,
        event_dispatcher: Optional[Callable[[dict], Awaitable[None]]] = None,
        **config,
    ):
        super().__init__(**config)
        self._uri = uri or ncatbot_config.get_uri_with_token()
        self._event_dispatcher = event_dispatcher

        self._ws: Optional[NapCatWebSocket] = None

        # 使用 Future 存储挂起的请求
        # Key: echo (str), Value: asyncio.Future
        self._pending_futures: Dict[str, asyncio.Future] = {}
        # 线程锁，保护 _pending_futures 的并发访问
        self._futures_lock = threading.Lock()

    async def on_load(self) -> None:
        self._loop = asyncio.get_running_loop()
        self._ws = NapCatWebSocket(
            uri=self._uri,
            message_callback=self._on_message,
        )
        await self._ws.connect()
        LOG.info("消息路由服务已加载")

    async def on_close(self) -> None:
        # 清理所有正在等待的 Future，防止调用方永久卡死
        with self._futures_lock:
            for future in self._pending_futures.values():
                if not future.done():
                    future.cancel()
            self._pending_futures.clear()

        if self._ws:
            await self._ws.disconnect()
            self._ws = None

        LOG.info("消息路由服务已关闭")

    @property
    def connected(self) -> bool:
        return self._ws is not None and self._ws.connected

    @property
    def websocket(self) -> Optional[NapCatWebSocket]:
        return self._ws

    def set_event_dispatcher(
        self, dispatcher: Callable[[dict], Awaitable[None]]
    ) -> None:
        self._event_dispatcher = dispatcher

    async def send(
        self,
        action: str,
        params: Optional[dict] = None,
        timeout: float = 30.0,
    ) -> dict:
        if not self._ws:
            raise ConnectionError("服务未连接")

        echo = str(uuid.uuid4())

        # 【关键改动 1】：Future 必须创建在“当前运行”的 Loop 上
        # 这样无论你在哪个线程执行 asyncio.run，await 都能成功
        current_loop = asyncio.get_running_loop()
        future = current_loop.create_future()

        with self._futures_lock:
            self._pending_futures[echo] = future

        async def _do_send():
            await self._ws.send(
                {
                    "action": action.replace("/", ""),
                    "params": params or {},
                    "echo": echo,
                }
            )

        try:
            # 【关键改动 2】：将发送逻辑塞回持有 WebSocket 的那个主 _loop
            # 这确保了底层 WebSocket 对象的线程安全
            if current_loop == self._loop:
                await _do_send()
            else:
                asyncio.run_coroutine_threadsafe(_do_send(), self._loop)

            return await asyncio.wait_for(future, timeout=timeout)
        except asyncio.TimeoutError:
            raise TimeoutError(f"API请求超时: {action}")
        finally:
            with self._futures_lock:
                self._pending_futures.pop(echo, None)

    def start_listening(self):
        if self._ws:
            return self._ws.start_listening()

    async def _on_message(self, data: dict) -> None:
        """处理收到的消息"""
        # 这个函数不是线程安全的, Client 必须和它在同一个线程
        echo = data.get("echo")

        # 优先检查是否是 API 响应
        if echo:
            # 线程安全地获取 Future
            with self._futures_lock:
                future = self._pending_futures.get(echo)
            if future and not future.done():
                # 使用 call_soon_threadsafe 确保跨线程安全设置结果
                future.get_loop().call_soon_threadsafe(future.set_result, data)
                return

        # 如果不是响应，或者找不到 echo，则视为事件
        if self._event_dispatcher:
            asyncio.ensure_future(self._event_dispatcher(data))
