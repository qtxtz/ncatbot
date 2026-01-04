"""配置模块 - 导出公共接口。

架构：
- models.py: 数据模型层 - Pydantic 模型与校验
- storage.py: 存储层 - 配置文件的读写
- manager.py: 管理层 - 对外暴露的唯一接口

"""

from .manager import get_config_manager
from .storage import CONFIG_PATH

# 兼容别名：ncatbot_config 指向单例管理器
ncatbot_config = get_config_manager()

__all__ = [
    # 管理层（主要接口）
    "ncatbot_config",
    # 常量
    "CONFIG_PATH",
]
