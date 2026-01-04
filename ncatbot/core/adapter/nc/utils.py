"""
通用工具函数

提供文件下载、解压、版本检查等通用功能。
"""

import os
import site
import subprocess
import sys
import zipfile
from typing import Optional

import urllib.parse
import socket
import json
import urllib.request
import urllib.error
from tqdm import tqdm
from pathlib import Path
from ncatbot.utils import global_status, get_log

LOG = get_log("Adapter")


# ==================== 文件操作 ====================


def download_file(url: str, file_path: Path) -> None:
    """
    下载文件（带进度条）

    Args:
        url: 下载地址
        file_name: 保存的文件名
    """
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ncatbot/1.0"})
        with urllib.request.urlopen(req) as response:
            total_size = int(response.headers.get("Content-Length", 0))

            progress_bar = tqdm(
                total=total_size,
                unit="iB",
                unit_scale=True,
                desc=f"Downloading {file_path}",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
                colour="green",
                dynamic_ncols=True,
                smoothing=0.3,
                mininterval=0.1,
                maxinterval=1.0,
            )

            with open(file_path, "wb") as f:
                while True:
                    data = response.read(1024)
                    if not data:
                        break
                    progress_bar.update(len(data))
                    f.write(data)

            progress_bar.close()
    except Exception as e:
        LOG.error(f"从 {url} 下载 {file_path} 失败: {e}")
        raise


def unzip_file(file_path: Path, extract_path: Path, remove: bool = False) -> None:
    """
    解压 ZIP 文件

    Args:
        file_name: ZIP 文件路径
        extract_path: 解压目标路径
        remove: 解压后是否删除 ZIP 文件
    """
    try:
        with zipfile.ZipFile(file_path, "r") as zip_ref:
            zip_ref.extractall(extract_path)
            LOG.info(f"解压 {file_path} 成功")

        if remove:
            os.remove(file_path)
    except Exception as e:
        LOG.error(f"解压 {file_path} 失败: {e}")
        raise


# ==================== 版本检查 ====================


def get_local_package_version(package_name: str) -> Optional[str]:
    """
    获取已安装包的版本

    Args:
        package_name: 包名

    Returns:
        版本号字符串，未安装返回 None
    """
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        for line in result.stdout.splitlines():
            if line.lower().startswith(package_name.lower()):
                parts = line.split()
                if len(parts) >= 2:
                    return parts[1]
        return None
    except subprocess.CalledProcessError:
        return None


def get_pypi_latest_version(package_name: str) -> Optional[str]:
    """
    获取 PyPI 上的最新版本

    Args:
        package_name: 包名

    Returns:
        最新版本号，获取失败返回 None
    """
    try:
        url = urllib.parse.urljoin(
            "https://mirrors.aliyun.com/pypi/simple/", f"{package_name}/json"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "ncatbot/1.0"})
        with urllib.request.urlopen(req, timeout=3) as response:
            data = response.read()
            result = json.loads(data.decode("utf-8"))
            return result["info"]["version"]
    except Exception:
        return None


def is_package_installed(package_name: str) -> bool:
    """
    检查包是否已安装

    Args:
        package_name: 包名

    Returns:
        是否已安装
    """
    all_paths = site.getsitepackages() + [site.getusersitepackages()]

    for path in all_paths:
        # 检查包目录
        if os.path.exists(os.path.join(path, package_name)):
            return True
        # 检查 egg-info
        if os.path.exists(os.path.join(path, f"{package_name}.egg-info")):
            return True

    return False


def check_self_package_version() -> bool:
    """
    检查当前包的版本

    Returns:
        True 如果包已正确安装
    """
    package_name = "ncatbot"

    if not is_package_installed(package_name):
        LOG.error(f"包 {package_name} 未使用 pip 安装")
        return False

    local_version = get_local_package_version(package_name)
    if not local_version:
        LOG.error(f"包 {package_name} 未使用 pip 安装")
        return False

    latest_version = get_pypi_latest_version(package_name)
    if not latest_version:
        LOG.warning("获取 NcatBot 最新版本失败")
        return True

    if local_version != latest_version:
        LOG.warning("NcatBot 有可用更新！")
        LOG.info("若使用 main.exe 或 NcatBot CLI 启动, CLI 输入 update 即可更新")
        LOG.info("若手动安装, 推荐使用: pip install --upgrade ncatbot")

    return True


# ==================== 网络请求 ====================


def post_json(
    url: str,
    payload: Optional[dict] = None,
    headers: Optional[dict] = None,
    timeout: float = 5.0,
) -> dict:
    body = None
    req_headers = {
        "User-Agent": "ncatbot/1.0",
        "Accept": "application/json",
    }
    if headers:
        req_headers.update(headers)
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        req_headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=req_headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", resp.getcode())
            if status != 200:
                raise urllib.error.HTTPError(
                    url, status, "Non-200 response", hdrs=resp.headers, fp=None
                )
            data = resp.read()
            return json.loads(data.decode("utf-8"))
    except socket.timeout as e:
        # 维持与原代码的 TimeoutError 语义一致
        raise TimeoutError("request timed out") from e
    except urllib.error.URLError as e:
        # 某些实现会把超时包裹在 URLError.reason 中
        if isinstance(getattr(e, "reason", None), socket.timeout):
            raise TimeoutError("request timed out") from e
        raise


def get_json(url: str, headers: Optional[dict] = None, timeout: float = 5.0) -> dict:
    req_headers = {
        "User-Agent": "ncatbot/1.0",
        "Accept": "application/json",
    }
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", resp.getcode())
            if status != 200:
                raise urllib.error.HTTPError(
                    url, status, "Non-200 response", hdrs=resp.headers, fp=None
                )
            data = resp.read()
            return json.loads(data.decode("utf-8"))
    except socket.timeout as e:
        # 维持与原代码的 TimeoutError 语义一致
        raise TimeoutError("request timed out") from e
    except urllib.error.URLError as e:
        # 某些实现会把超时包裹在 URLError.reason 中
        if isinstance(getattr(e, "reason", None), socket.timeout):
            raise TimeoutError("request timed out") from e
        raise


def get_proxy_url():
    """获取 github 代理 URL"""
    if global_status.current_github_proxy is not None:
        return global_status.current_github_proxy
    TIMEOUT = 10
    github_proxy_urls = [
        "https://ghfast.top/",
        # "https://github.7boe.top/",
        # "https://cdn.moran233.xyz/",
        # "https://gh-proxy.ygxz.in/",
        # "https://github.whrstudio.top/",
        # "https://proxy.yaoyaoling.net/",
        # "https://ghproxy.net/",
        # "https://fastgit.cc/",
        # "https://git.886.be/",
        # "https://gh-proxy.com/",
    ]
    available_proxy = []

    def check_proxy(url):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "ncatbot/1.0"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as response:
                if response.getcode() == 200:
                    return url
        except socket.timeout as e:
            LOG.warning(f"请求失败: {url}, 错误: {e}")
            return None
        except Exception:
            return None

    url = check_proxy(github_proxy_urls[0])
    if url is not None:
        available_proxy.append(url)

    if len(available_proxy) > 0:
        global_status.current_github_proxy = available_proxy[0]
        return available_proxy[0]
    else:
        LOG.warning("无法连接到任何 GitHub 代理, 将直接连接 GitHub")
        global_status.current_github_proxy = None
        return ""


def gen_url_with_proxy(original_url: str) -> str:
    """生成带代理的 URL"""
    proxy_url = get_proxy_url()
    return (
        f"{proxy_url.strip('/')}/{original_url.strip('/')}"
        if proxy_url
        else original_url
    )
