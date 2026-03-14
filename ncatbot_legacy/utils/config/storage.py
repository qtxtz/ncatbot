"""配置存储层 - 负责配置文件的读写操作。"""

import os
import yaml
from typing import Any, Dict, Optional
from .models import Config

CONFIG_PATH = os.getenv("NCATBOT_CONFIG_PATH", os.path.join(os.getcwd(), "config.yaml"))

class ConfigStorage:
    """配置文件存储管理。"""

    def __init__(self, path: Optional[str] = None):
        self.path = path or CONFIG_PATH

    def load(self) -> Config:
        """加载配置，文件不存在则返回默认配置。"""
        data = self._load_raw()
        return Config.model_validate(data)

    def save(self, config: Config) -> None:
        """保存配置到文件。"""
        self._save_raw(config.to_dict())

    def exists(self) -> bool:
        """检查配置文件是否存在。"""
        return os.path.exists(self.path)

    def _load_raw(self) -> Dict[str, Any]:
        """读取原始配置数据。"""
        if not os.path.exists(self.path):
            return {}

        with open(self.path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def _save_raw(self, data: Dict[str, Any]) -> None:
        """写入原始配置数据，使用原子写入。"""
        dir_path = os.path.dirname(self.path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)

        tmp_path = f"{self.path}.tmp"
        with open(tmp_path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)

        os.replace(tmp_path, self.path)
