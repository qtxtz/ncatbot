"""通用网络工具 — JSON 请求、文件下载、GitHub 代理。"""

import json
import socket
import urllib
import urllib.error
import urllib.request
from typing import Optional

from .logger import get_log

_log = get_log()

# 模块级缓存，替代 legacy 中 status.current_github_proxy
_cached_github_proxy: Optional[str] = None
_proxy_resolved: bool = False


def post_json(
    url: str,
    payload: Optional[dict] = None,
    headers: Optional[dict] = None,
    timeout: float = 5.0,
) -> dict:
    """发送 JSON POST 请求并返回解析后的字典。"""
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
        raise TimeoutError("request timed out") from e
    except urllib.error.URLError as e:
        if isinstance(getattr(e, "reason", None), socket.timeout):
            raise TimeoutError("request timed out") from e
        raise


def get_json(url: str, headers: Optional[dict] = None, timeout: float = 5.0) -> dict:
    """发送 JSON GET 请求并返回解析后的字典。"""
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
        raise TimeoutError("request timed out") from e
    except urllib.error.URLError as e:
        if isinstance(getattr(e, "reason", None), socket.timeout):
            raise TimeoutError("request timed out") from e
        raise


def download_file(url: str, file_name: str) -> None:
    """下载文件（带进度条）。"""
    import requests
    from tqdm import tqdm

    r = requests.get(url, stream=True)
    total_size = int(r.headers.get("content-length", 0))
    progress_bar = tqdm(
        total=total_size,
        unit="iB",
        unit_scale=True,
        desc=f"Downloading {file_name}",
        bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
        colour="green",
        dynamic_ncols=True,
        smoothing=0.3,
        mininterval=0.1,
        maxinterval=1.0,
    )
    with open(file_name, "wb") as f:
        for data in r.iter_content(chunk_size=1024):
            progress_bar.update(len(data))
            f.write(data)
    progress_bar.close()


def get_proxy_url() -> str:
    """获取 GitHub 代理 URL（结果会缓存）。"""
    import requests

    global _cached_github_proxy, _proxy_resolved
    if _proxy_resolved:
        return _cached_github_proxy or ""

    github_proxy_urls = [
        "https://ghfast.top/",
    ]

    for proxy in github_proxy_urls:
        try:
            response = requests.get(proxy, timeout=10)
            if response.status_code == 200:
                _cached_github_proxy = proxy
                _proxy_resolved = True
                return proxy
        except TimeoutError:
            _log.warning(f"代理请求超时: {proxy}")
        except Exception:
            pass

    _log.warning("无法连接到任何 GitHub 代理, 将直接连接 GitHub")
    _cached_github_proxy = None
    _proxy_resolved = True
    return ""


def gen_url_with_proxy(original_url: str) -> str:
    """生成带 GitHub 代理前缀的 URL。"""
    proxy_url = get_proxy_url()
    return (
        f"{proxy_url.strip('/')}/{original_url.strip('/')}"
        if proxy_url
        else original_url
    )
