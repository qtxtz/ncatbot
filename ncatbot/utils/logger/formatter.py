"""日志格式化器。"""

import logging

from ncatbot.utils.assets.color import Color

CONSOLE_FORMATS = {
    "DEBUG": (
        f"{Color.CYAN}[%(asctime)s.%(msecs)03d]{Color.RESET} "
        f"{Color.BLUE}%(levelname)-8s{Color.RESET} "
        f"{Color.MAGENTA}%(name)s{Color.RESET} "
        f"{Color.YELLOW}'%(filename)s:%(lineno)d'{Color.RESET} "
        "| %(message)s"
    ),
    "INFO": (
        f"{Color.CYAN}[%(asctime)s.%(msecs)03d]{Color.RESET} "
        f"{Color.GREEN}%(levelname)-8s{Color.RESET} "
        f"{Color.MAGENTA}%(name)s{Color.RESET} "
        f"{Color.GRAY}'%(filename)s:%(lineno)d'{Color.RESET} ➜ "
        f"{Color.WHITE}%(message)s{Color.RESET}"
    ),
    "WARNING": (
        f"{Color.CYAN}[%(asctime)s.%(msecs)03d]{Color.RESET} "
        f"{Color.YELLOW}%(levelname)-8s{Color.RESET} "
        f"{Color.MAGENTA}%(name)s{Color.RESET} "
        f"{Color.GRAY}'%(filename)s:%(lineno)d'{Color.RESET} "
        f"{Color.RED}➜{Color.RESET} "
        f"{Color.YELLOW}%(message)s{Color.RESET}"
    ),
    "ERROR": (
        f"{Color.CYAN}[%(asctime)s.%(msecs)03d]{Color.RESET} "
        f"{Color.RED}%(levelname)-8s{Color.RESET} "
        f"{Color.GRAY}'%(filename)s:%(lineno)d'{Color.RESET}"
        f"{Color.MAGENTA} %(name)s{Color.RESET} "
        f"{Color.RED}➜{Color.RESET} "
        f"{Color.RED}%(message)s{Color.RESET}"
    ),
    "CRITICAL": (
        f"{Color.CYAN}[%(asctime)s.%(msecs)03d]{Color.RESET} "
        f"{Color.BG_RED}{Color.WHITE}%(levelname)-8s{Color.RESET} "
        f"{Color.GRAY}{{%(module)s}}{Color.RESET}"
        f"{Color.MAGENTA} '%(filename)s:%(lineno)d'{Color.RESET}"
        f"{Color.MAGENTA} %(name)s{Color.RESET} "
        f"{Color.BG_RED}➜{Color.RESET} "
        f"{Color.BOLD}%(message)s{Color.RESET}"
    ),
}

FILE_FORMAT = (
    "[%(asctime)s.%(msecs)03d] %(levelname)-8s %(name)s "
    "'%(filename)s:%(lineno)d' ➜ %(message)s"
)


class ColoredFormatter(logging.Formatter):
    """根据日志级别动态切换格式模板的控制台 Formatter。"""

    def __init__(self, datefmt: str = "%H:%M:%S"):
        super().__init__(datefmt=datefmt)
        self._formatters = {
            level: logging.Formatter(fmt, datefmt=datefmt)
            for level, fmt in CONSOLE_FORMATS.items()
        }
        self._default = logging.Formatter(CONSOLE_FORMATS["INFO"], datefmt=datefmt)

    def format(self, record: logging.LogRecord) -> str:
        formatter = self._formatters.get(record.levelname, self._default)
        return formatter.format(record)


class FileFormatter(logging.Formatter):
    """文件日志 Formatter，无颜色码。"""

    def __init__(self, datefmt: str = "%Y-%m-%d %H:%M:%S"):
        super().__init__(FILE_FORMAT, datefmt=datefmt)
