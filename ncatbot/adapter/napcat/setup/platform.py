"""
平台操作抽象层

使用工厂模式统一 Windows/Linux 平台的 NapCat 目录、启动、停止操作。
安装逻辑已提取到 installer.py。
"""

import json
import os
import platform
import subprocess
import sys
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from ncatbot.utils import get_log
from ncatbot.adapter.napcat.constants import LINUX_NAPCAT_DIR, WINDOWS_NAPCAT_DIR

LOG = get_log("NapCatPlatform")


class UnsupportedPlatformError(Exception):
    """不支持的操作系统"""

    def __init__(self, system: Optional[str] = None):
        system = system or platform.system()
        super().__init__(f"不支持的操作系统: {system}")


class PlatformOps(ABC):
    """平台操作抽象基类"""

    @staticmethod
    def create() -> "PlatformOps":
        system = platform.system()
        if system == "Windows":
            return WindowsOps()
        elif system == "Linux":
            return LinuxOps()
        raise UnsupportedPlatformError(system)

    @property
    @abstractmethod
    def napcat_dir(self) -> Path: ...

    @property
    def config_dir(self) -> Path:
        return self.napcat_dir / "config"

    @abstractmethod
    def is_napcat_running(self, uin: Optional[str] = None) -> bool: ...

    @abstractmethod
    def start_napcat(self, uin: str) -> None: ...

    @abstractmethod
    def stop_napcat(self) -> None: ...

    def is_napcat_installed(self) -> bool:
        return self.napcat_dir.exists()

    def get_installed_version(self) -> Optional[str]:
        package_json = self.napcat_dir / "package.json"
        if not package_json.exists():
            return None
        try:
            with open(package_json, "r", encoding="utf-8") as f:
                return json.load(f)["version"]
        except (json.JSONDecodeError, KeyError):
            return None

    @staticmethod
    def _confirm_action(prompt: str) -> bool:
        return input(prompt).strip().lower() in ["y", "yes"]


class WindowsOps(PlatformOps):
    """Windows 平台操作"""

    @property
    def napcat_dir(self) -> Path:
        return Path(WINDOWS_NAPCAT_DIR)

    def is_napcat_running(self, uin: Optional[str] = None) -> bool:
        return True

    def start_napcat(self, uin: str) -> None:
        launcher = self._get_launcher_name()
        launcher_path = self.napcat_dir / launcher

        if not launcher_path.exists():
            raise FileNotFoundError(f"找不到启动文件: {launcher_path}")

        LOG.info(f"正在启动 QQ, 启动器路径: {launcher_path}")
        subprocess.Popen(
            f'"{launcher_path}" {uin}',
            shell=True,
            cwd=str(self.napcat_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    def stop_napcat(self) -> None:
        try:
            subprocess.run(
                ["taskkill", "/F", "/IM", "QQ.exe"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            LOG.info("已成功停止 QQ.exe 进程")
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode(errors="ignore") if e.stderr else ""
            LOG.error(f"停止 NapCat 服务失败: {stderr}")
            raise RuntimeError(f"无法停止 QQ.exe 进程: {stderr}")

    def _get_launcher_name(self) -> str:
        platform_info = platform.platform()

        try:
            edition = platform.win32_edition()
            is_server = "Server" in edition
        except AttributeError:
            is_server = "Server" in platform_info

        if is_server:
            if any(ver in platform_info for ver in ["2016", "2019", "2022"]):
                LOG.info("当前操作系统: Windows Server (旧版本)")
                return "launcher-win10.bat"
            elif "2025" in platform_info:
                LOG.info("当前操作系统: Windows Server 2025")
                return "launcher.bat"
            LOG.warning("不支持的 Windows Server 版本，按 Windows 10 内核启动")
            return "launcher-win10.bat"

        release = platform.release()
        if release == "11":
            LOG.info("当前操作系统: Windows 11")
            return "launcher.bat"

        LOG.info("当前操作系统: Windows 10")
        return "launcher-win10.bat"


class LinuxOps(PlatformOps):
    """Linux 平台操作"""

    @property
    def napcat_dir(self) -> Path:
        target = Path(LINUX_NAPCAT_DIR)
        if target.exists():
            return target
        return Path.home() / "Napcat/opt/QQ/resources/app/app_launcher/napcat"

    def is_napcat_running(self, uin: Optional[str] = None) -> bool:
        process = subprocess.Popen(["bash", "napcat", "status"], stdout=subprocess.PIPE)
        process.wait()
        stdout = process.stdout
        if stdout is None:
            return False
        output = stdout.read().decode(encoding="utf-8")

        if uin is None:
            return "PID" in output
        return str(uin) in output

    def start_napcat(self, uin: str) -> None:
        if self.is_napcat_running(uin):
            LOG.info("NapCat 已启动")
            return

        if self.is_napcat_running():
            LOG.warning("NapCat 正在运行, 但运行的不是该 QQ 号")
            if input("按 y 强制结束当前进程并继续, 按其他键退出: ") == "y":
                self.stop_napcat()
            else:
                raise RuntimeError("NapCat 正在运行, 但运行的不是该 QQ 号")

        if os.path.exists("napcat"):
            LOG.error("工作目录下存在 napcat 目录")
            raise FileExistsError("工作目录下存在 napcat 目录")

        LOG.info("正在启动 NapCat 服务")
        process = subprocess.Popen(
            ["sudo", "bash", "napcat", "start", uin],
            stdout=subprocess.PIPE,
        )
        process.wait()

        if process.returncode != 0:
            LOG.error(f"启动失败，请检查目录 {LINUX_NAPCAT_DIR}")
            raise FileNotFoundError("napcat cli 可能没有被正确安装")

        if not self.is_napcat_running(uin):
            raise RuntimeError("napcat 启动失败")

        time.sleep(0.5)
        LOG.info("napcat 启动成功")

    def stop_napcat(self) -> None:
        try:
            process = subprocess.Popen(
                ["bash", "napcat", "stop"], stdout=subprocess.PIPE
            )
            process.wait()
            if process.returncode != 0:
                raise RuntimeError("停止 napcat 失败")
            LOG.info("已成功停止 napcat")
        except Exception as e:
            LOG.error(f"停止 napcat 失败: {e}")
            raise

    @staticmethod
    def _check_root() -> bool:
        try:
            result = subprocess.run(
                ["sudo", "whoami"],
                check=True,
                text=True,
                capture_output=True,
            )
            return result.stdout.strip() == "root"
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
