"""配置管理层 - 对外暴露的唯一接口。"""

from typing import List, Optional

from .models import Config, NapCatConfig, PluginConfig
from .storage import ConfigStorage


class ConfigValueError(Exception):
    def __init__(self, msg) -> None:
        super().__init__(f"配置项错误: {msg}")

class UinValueError(ConfigValueError):
    def __init__(self, value: str):
        super().__init__(f"QQ 号必须是整数数字, 但读到 {value}")

def ensure_uin(value):
    value = str(value)
    if not value.isdigit():
        raise UinValueError(value)
    return value

class ConfigManager:
    """配置管理器，提供配置的读写接口。"""

    def __init__(self, path: Optional[str] = None):
        self._storage = ConfigStorage(path)
        self._config: Optional[Config] = None

    @property
    def config(self) -> Config:
        """获取配置对象，懒加载。"""
        if self._config is None:
            self._config = self._storage.load()
        return self._config

    def reload(self) -> Config:
        """重新加载配置。"""
        self._config = self._storage.load()
        return self._config

    def save(self) -> None:
        """保存当前配置。"""
        if self._config is not None:
            self._storage.save(self._config)

    # ==================== NapCat 配置 ====================

    @property
    def napcat(self) -> NapCatConfig:
        return self.config.napcat

    def set_ws_uri(self, value: str) -> None:
        self.napcat.ws_uri = value

    def set_ws_token(self, value: str) -> None:
        self.napcat.ws_token = value

    def set_webui_uri(self, value: str) -> None:
        self.napcat.webui_uri = value

    def set_webui_token(self, value: str) -> None:
        self.napcat.webui_token = value

    def set_webui_enabled(self, value: bool) -> None:
        self.napcat.enable_webui = value

    # ==================== 插件配置 ====================

    @property
    def plugin(self) -> PluginConfig:
        return self.config.plugin

    def get_plugins_dir(self) -> str:
        return self.plugin.plugins_dir

    def set_plugins_dir(self, value: str) -> None:
        self.plugin.plugins_dir = value

    # ==================== 主配置 ====================

    @property
    def bot_uin(self) -> str:
        return self.config.bt_uin

    @property
    def root(self) -> str:
        return self.config.root
    
    @property
    def debug(self) -> bool:
        return self.config.debug
    
    @debug.setter
    def debug(self, value: bool) -> None:
        self.config.debug = value

    def set_bot_uin(self, value: str) -> None:
        self.config.bt_uin = ensure_uin(value)
    
    def set_root(self, value: str) -> None:
        self.config.root = ensure_uin(value)

    def set_debug(self, value: bool) -> None:
        self.config.debug = value

    # ==================== 工具方法 ====================

    def get_issues(self) -> List[str]:
        """校验安全性，返回问题列表。"""
        issues = []
        issues.extend(self.napcat.get_issues())
        if self.is_default_uin():
            issues.append("机器人 QQ 号未配置, 无法正常登录")
        if self.is_default_root():
            issues.append("管理员 QQ 号未配置, 无法使用部分管理功能")
        return issues

    def is_local(self) -> bool:
        """NapCat 是否为本地服务。"""
        return self.config.is_local()

    def is_default_uin(self) -> bool:
        """是否使用默认 QQ 号。"""
        return self.config.is_default_uin()

    def is_default_root(self) -> bool:
        """是否使用默认管理员 QQ 号。"""
        return self.config.is_default_root()

    def ensure_plugins_dir(self) -> None:
        """确保插件目录存在。"""
        self.plugin.ensure_dir_exists()

    def fix_invalid_config(self):
        """修复无效配置，提示用户输入。
        
        Args:
            auto_mode: 是否启用自动模式（对应 --auto 参数）
        """ 
        if self.is_default_uin():
            for _ in range(3):
                try:
                    self.set_bot_uin(ensure_uin(input("请输入您的机器人 QQ 号:")))
                    break
                except UinValueError:
                    pass
            else:
                raise ConfigValueError("不正确的 QQ 号")
                
        if self.napcat.get_security_issues(auto_fix=False):
            if input("NapCat Token 强度不足, 是否自动修复").lower() in ['y', "yes"]:
                self.napcat.fix_security_issues()
            else:
                raise ValueError("NapCat Token 强度不足, 拒绝启动")

# 默认管理器实例
_default_manager: Optional[ConfigManager] = None


def get_config_manager(path: Optional[str] = None) -> ConfigManager:
    """获取配置管理器单例。"""
    global _default_manager
    if _default_manager is None or path is not None:
        _default_manager = ConfigManager(path)
    return _default_manager
