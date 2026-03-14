"""NcatBot 工具包。

已迁移模块：logger / config / network
仍通过 __path__ 代理的模块：status / error / assets
"""

import sys as _sys
from pathlib import Path as _Path

# ── legacy 子模块仍需 __path__ 代理（追加到末尾，新包优先） ──
_legacy_utils = str(
    _Path(__file__).resolve().parent.parent.parent / "ncatbot_legacy" / "utils"
)
if _legacy_utils not in __path__:
    __path__.append(_legacy_utils)

# ── 已迁移模块：从本包新实现导入 ──
from .logger import get_log, BoundLogger, setup_logging, tqdm  # noqa
from .config import (  # noqa
    ConfigManager,
    get_config_manager,
    Config,
    CONFIG_PATH,
    ConfigValueError,
)
from .network import (  # noqa
    post_json,
    get_json,
    download_file,
    get_proxy_url,
    gen_url_with_proxy,
)

# ── 未迁移模块：仍从 legacy 代理 ──
from .status import Status, status  # noqa
from .error import NcatBotError, NcatBotValueError, NcatBotConnectionError  # noqa
from .assets import *  # noqa: F401,F403

# 注册双名称，防止 legacy 代理模块被重复加载
for _sub in (
    "status",
    "error",
    "assets",
    "assets.color",
    "assets.literals",
):
    _new = f"ncatbot.utils.{_sub}"
    _old = f"ncatbot_legacy.utils.{_sub}"
    _mod = _sys.modules.get(_new)
    if _mod is not None and _old not in _sys.modules:
        _sys.modules[_old] = _mod

ncatbot_config = get_config_manager()

__all__ = [
    "ncatbot_config",
    "Config",
    "ConfigManager",
    "get_config_manager",
    "ConfigValueError",
    "CONFIG_PATH",
    "get_log",
    "BoundLogger",
    "setup_logging",
    "tqdm",
    "status",
    "Status",
    "post_json",
    "get_json",
    "download_file",
    "get_proxy_url",
    "gen_url_with_proxy",
    "NcatBotError",
    "NcatBotValueError",
    "NcatBotConnectionError",
]
