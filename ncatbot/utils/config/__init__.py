from .manager import ConfigManager, get_config_manager, ConfigValueError
from .models import Config, NapCatConfig, PluginConfig, BaseConfig, AdapterEntry
from .storage import ConfigStorage, CONFIG_PATH
from .security import strong_password_check, generate_strong_token

# 兼容别名：legacy 模块通过 from .config import ncatbot_config 引用
ncatbot_config = get_config_manager()

__all__ = [
    "ConfigManager",
    "get_config_manager",
    "ConfigValueError",
    "Config",
    "NapCatConfig",
    "PluginConfig",
    "BaseConfig",
    "AdapterEntry",
    "ConfigStorage",
    "CONFIG_PATH",
    "strong_password_check",
    "generate_strong_token",
    "ncatbot_config",
]
