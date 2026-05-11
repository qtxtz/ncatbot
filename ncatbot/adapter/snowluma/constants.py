"""SnowLuma 适配器专用常量。"""

from __future__ import annotations

# ==================== 安装目录 ====================

#: Windows 平台默认安装目录（相对当前工作目录，与 napcat 一致放在工作区下）。
WINDOWS_SNOWLUMA_DIR = "snowluma"

# ==================== Release 资源 ====================

#: GitHub 仓库（用户/仓库名）
SNOWLUMA_REPO = "SnowLuma/SnowLuma"

#: 最新 release 重定向 URL（用 HEAD 请求 + follow_redirects 拿版本号）
SNOWLUMA_LATEST_RELEASE_URL = (
    f"https://github.com/{SNOWLUMA_REPO}/releases/latest"
)

#: GitHub Tags API（备选，受 API 限额影响）
SNOWLUMA_TAGS_API_URL = f"https://api.github.com/repos/{SNOWLUMA_REPO}/tags"


def windows_asset_url(version: str, *, lite: bool = False) -> str:
    """构造 Windows x64 release 资产下载 URL。

    Parameters
    ----------
    version:
        版本号，可带或不带 ``v`` 前缀（如 ``"1.7.5"`` 或 ``"v1.7.5"``）。
    lite:
        是否使用 lite 包（不含可选依赖，体积更小）。
    """
    v = version.lstrip("v")
    suffix = "-lite" if lite else ""
    return (
        f"https://github.com/{SNOWLUMA_REPO}/releases/download/"
        f"v{v}/SnowLuma-v{v}-win-x64{suffix}.zip"
    )


# ==================== 默认端口 ====================

#: SnowLuma 默认 WebUI 端口（runtime.json 中的 webuiPort，与 NapCat 6099 区分）
DEFAULT_WEBUI_PORT = 5099

#: SnowLuma 默认 OneBot v11 WebSocket 端口（与 NapCat 一致，由用户在 WebUI 中设置）
DEFAULT_WS_PORT = 3001
