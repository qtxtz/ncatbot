"""
平台适配器抽象基类
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable, Awaitable, List, TYPE_CHECKING

if TYPE_CHECKING:
    from ncatbot.api.interface import IBotAPI
    from ncatbot.types import BaseEventData


class BaseAdapter(ABC):
    """平台适配器抽象基类

    回调签名为 Callable[[BaseEventData], Awaitable[None]]，
    即 adapter 只产出纯数据模型，不创建实体。
    """

    name: str
    description: str
    supported_protocols: List[str]

    _event_callback: Optional[Callable[["BaseEventData"], Awaitable[None]]] = None

    # ---- 生命周期 ----

    @abstractmethod
    async def setup(self) -> None:
        """准备平台环境（安装/配置/启动）"""

    @abstractmethod
    async def connect(self) -> None:
        """建立连接并初始化 API"""

    @abstractmethod
    async def disconnect(self) -> None:
        """断开连接，释放资源"""

    @abstractmethod
    async def listen(self) -> None:
        """阻塞监听消息，内部完成事件解析后回调数据模型"""

    # ---- API ----

    @abstractmethod
    def get_api(self) -> "IBotAPI":
        """返回 IBotAPI 实现"""

    # ---- 回调 ----

    def set_event_callback(
        self, callback: Callable[["BaseEventData"], Awaitable[None]],
    ) -> None:
        """设置事件数据回调，由异步分发器在启动时调用"""
        self._event_callback = callback

    # ---- 状态 ----

    @property
    @abstractmethod
    def connected(self) -> bool: ...
