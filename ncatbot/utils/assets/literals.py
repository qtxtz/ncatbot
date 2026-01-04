# 字面常量
from enum import Enum

INSTALL_SCRIPT_URL = (
    "https://nclatest.znin.net/NapNeko/NapCat-Installer/main/script/install.sh"
)
NAPCAT_CLI_URL = (
    "https://nclatest.znin.net/NapNeko/NapCat-Installer/main/script/napcat_cli"
)
PYPI_URL = "https://mirrors.aliyun.com/pypi/simple/"


class PermissionGroup(Enum):
    # 权限组常量
    ROOT = "root"
    ADMIN = "admin"
    USER = "user"


class DefaultPermission(Enum):
    # 权限常量
    ACCESS = "access"
    SETADMIN = "setadmin"


PLUGINS_DIR = "plugins"  # 插件目录

__all__ = [
    "INSTALL_SCRIPT_URL",
    "NAPCAT_CLI_URL",
    "PYPI_URL",
    "PermissionGroup",
    "DefaultPermission",
    "PLUGINS_DIR",
]
