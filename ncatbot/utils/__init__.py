"""NcatBot 工具包"""

from .config import ConfigManager, get_config_manager, Config, CONFIG_PATH
from .logger import get_log
from .status import Status, status
from .network_io import gen_url_with_proxy, get_json, post_json
from .error import NcatBotError, NcatBotValueError, NcatBotConnectionError
from .assets import *  # noqa: F401,F403

# 兼容别名：ncatbot_config 指向单例管理器
ncatbot_config = get_config_manager()

__all__ = [
    "ncatbot_config",
    "Config",
    "ConfigManager",
    "get_config_manager",
    "CONFIG_PATH",
    "get_log",
    "status",
    "Status",
    "gen_url_with_proxy",
    "post_json",
    "get_json",
    "NcatBotError",
    "NcatBotValueError",
    "NcatBotConnectionError",
]
