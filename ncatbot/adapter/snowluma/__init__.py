"""SnowLuma 适配器 — 与 napcat 同级的 OneBot v11 协议端实现。

SnowLuma (https://github.com/SnowLuma/SnowLuma) 是基于 Node.js 的独立 OneBot v11
协议端，自带 Node 运行时、原生协议层和 WebUI（默认 5099 端口），不依赖系统
QQNT 客户端。NcatBot 仅作为 OneBot v11 客户端连接其 WebSocket 服务。

实现策略：
- 协议层（OB11Protocol / NapCatWebSocket / NapCatBotAPI / NapCatEventParser）完全
  复用 napcat 适配器的实现，不重复造轮子。
- ``setup/`` 子目录提供 SnowLuma 专用的下载、解压、启动逻辑，与 napcat 的
  ``setup/`` 互不影响。
- OneBot v11 的 WebSocket 服务与 QQ 登录由用户在 SnowLuma WebUI 中完成，本适配
  器不负责写入 OB11 配置文件或登录引导。
"""

from .adapter import SnowLumaAdapter
from .config import SnowLumaConfig

__all__ = ["SnowLumaAdapter", "SnowLumaConfig"]
