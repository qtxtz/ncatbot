"""
线程安全的异步运行器和同步方法生成器
"""

from __future__ import annotations

import asyncio
import atexit
import functools
import inspect
import threading
from typing import Any, Callable, Coroutine, Optional, TypeVar
from ncatbot.utils import get_log

T = TypeVar("T")
LOG = get_log("api")


class AsyncRunner:
    """
    线程安全的异步运行器（单例）

    管理一个后台事件循环，允许从任何线程（包括其他事件循环线程）安全地调用异步函数。

    使用场景：
    - 在同步代码中调用异步 API
    - 在一个事件循环中需要调用另一个事件循环的异步方法

    线程安全保证：
    - 使用独立的后台线程运行事件循环
    - 使用 run_coroutine_threadsafe 提交协程
    - 单例模式确保全局只有一个后台循环

    资源管理：
    - 使用 daemon 线程，程序退出时自动终止
    - 通过 atexit 注册清理函数，优雅关闭事件循环

    Example:
        ```python
        # 方式 1: 使用便捷函数
        result = run_sync(some_async_function())

        # 方式 2: 使用类方法
        runner = AsyncRunner.get_instance()
        result = runner.run(some_async_function())
        ```
    """

    _instance: Optional["AsyncRunner"] = None
    _lock = threading.Lock()
    _atexit_registered = False

    def __init__(self):
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._started = threading.Event()

    @classmethod
    def get_instance(cls) -> "AsyncRunner":
        """获取单例实例（懒加载，首次调用时启动后台循环）"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = cls()
                    instance._start()
                    cls._instance = instance
                    # 注册退出清理（仅注册一次）
                    if not cls._atexit_registered:
                        atexit.register(cls._cleanup)
                        cls._atexit_registered = True
        return cls._instance

    @classmethod
    def _cleanup(cls) -> None:
        """程序退出时自动调用的清理函数"""
        if cls._instance is not None:
            instance = cls._instance
            if instance._loop is not None:
                instance._loop.call_soon_threadsafe(instance._loop.stop)
            # daemon 线程会自动终止，无需 join
            cls._instance = None

    def _start(self) -> None:
        """启动后台事件循环线程"""
        self._thread = threading.Thread(
            target=self._run_loop,
            daemon=True,
            name="AsyncRunner-EventLoop",
        )
        self._thread.start()
        # 等待事件循环启动完成
        self._started.wait(timeout=10.0)
        if self._loop is None:
            raise RuntimeError("AsyncRunner 事件循环启动失败")

    def _run_loop(self) -> None:
        """后台线程入口：创建并运行事件循环"""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._started.set()
        self._loop.run_forever()
        # 清理
        self._loop.close()
        self._loop = None

    def run(self, coro: Coroutine[Any, Any, T], timeout: Optional[float] = None) -> T:
        """
        线程安全地运行协程并返回结果

        Args:
            coro: 要执行的协程
            timeout: 超时时间（秒），None 表示无限等待

        Returns:
            协程的返回值

        Raises:
            RuntimeError: 如果 AsyncRunner 未启动
            TimeoutError: 如果超时
            Exception: 协程内部抛出的任何异常
        """
        if asyncio.get_event_loop() is not None:
            LOG.warn("检测到正在运行的事件循环，建议直接使用异步接口")
        if self._loop is None:
            raise RuntimeError("AsyncRunner 未启动")

        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout)


def run_sync(coro: Coroutine[Any, Any, T], timeout: Optional[float] = None) -> T:
    """
    便捷函数：线程安全地运行协程

    在任何线程（包括事件循环线程）中调用异步函数的同步方式。

    Args:
        coro: 要执行的协程
        timeout: 超时时间（秒）

    Returns:
        协程的返回值

    Example:
        ```python
        # 同步调用异步 API
        info = run_sync(api.get_login_info())

        # 带超时
        result = run_sync(api.send_message(...), timeout=30.0)
        ```
    """
    return AsyncRunner.get_instance().run(coro, timeout)


def generate_sync_methods(cls: type) -> type:
    """
    类装饰器：为类中的所有公共异步方法自动生成同步版本

    同步方法名为原方法名加 `_sync` 后缀。

    特性：
    - 自动跳过私有方法（以 _ 开头）
    - 自动跳过已存在的同步方法
    - 同步方法线程安全，可在任何线程中调用
    - 保留原方法的文档字符串和签名信息

    Example:
        ```python
        @generate_sync_methods
        class MyAPI(APIComponent):
            async def get_info(self) -> dict:
                '''获取信息'''
                return await self._request("/get_info")

        # 自动生成:
        # def get_info_sync(self) -> dict:
        #     '''获取信息 (同步版本)'''
        #     return run_sync(self.get_info())
        ```

    Args:
        cls: 要装饰的类

    Returns:
        装饰后的类
    """
    for name in dir(cls):
        # 跳过私有方法和特殊方法
        if name.startswith("_"):
            continue

        method = getattr(cls, name, None)
        if method is None:
            continue

        # 只处理协程函数
        if not inspect.iscoroutinefunction(method):
            continue

        sync_name = f"{name}_sync"

        # 如果同步方法已存在，跳过
        if hasattr(cls, sync_name):
            continue

        # 创建同步包装器
        def make_sync_wrapper(async_method: Callable) -> Callable:
            @functools.wraps(async_method)
            def sync_wrapper(self, *args, **kwargs):
                coro = async_method(self, *args, **kwargs)
                return run_sync(coro)

            # 更新文档字符串
            if async_method.__doc__:
                sync_wrapper.__doc__ = async_method.__doc__ + "\n\n(同步版本)"
            else:
                sync_wrapper.__doc__ = "(同步版本)"

            return sync_wrapper

        setattr(cls, sync_name, make_sync_wrapper(method))

    return cls
