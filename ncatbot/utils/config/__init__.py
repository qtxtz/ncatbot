"""配置模块 - 导出公共接口。

架构：
- models.py: 数据模型层 - Pydantic 模型与校验
- storage.py: 存储层 - 配置文件的读写
- manager.py: 管理层 - 对外暴露的唯一接口

使用方式：
    from ncatbot.utils.config import ConfigManager, get_config_manager

    # 使用单例
    manager = get_config_manager()

    # 或创建新实例
    manager = ConfigManager("path/to/config.yaml")

    # 读写配置
    manager.set_ws_uri("ws://localhost:3001")
    manager.save()
"""

from .manager import ConfigManager, get_config_manager
from .models import Config, NapCatConfig, PluginConfig
from .storage import ConfigStorage, CONFIG_PATH
from .utils import generate_strong_password, strong_password_check

# 兼容别名：ncatbot_config 指向单例管理器
ncatbot_config = get_config_manager()

__all__ = [
    # 管理层（主要接口）
    "ConfigManager",
    "get_config_manager",
    "ncatbot_config",
    # 数据模型
    "Config",
    "NapCatConfig",
    "PluginConfig",
    # 存储层
    "ConfigStorage",
    # 工具函数
    "strong_password_check",
    "generate_strong_password",
    # 常量
    "CONFIG_PATH",
]
