"""Bilibili 扫码登录模块

通过 bilibili_api.login_v2.QrCodeLogin 实现终端扫码获取凭据。
在终端打印 ASCII 二维码，同时保存 PNG 图片供手机扫描。
"""

from __future__ import annotations

import asyncio
import os
import re
import tempfile
from typing import TYPE_CHECKING

from ncatbot.utils import get_log

if TYPE_CHECKING:
    from bilibili_api import Credential

LOG = get_log("BilibiliAuth")

# 匹配 ANSI CSI 序列（如 \x1b[0;37;47m）
_ANSI_RE = re.compile(r"\x1b\[([^m]*)m")


def _ansi_to_matrix(terminal_str: str) -> list[list[bool]]:
    """将 ANSI 彩色终端输出解析为布尔矩阵。

    bilibili_api 的 ``get_qrcode_terminal()`` 返回 ANSI 颜色序列：
    - 背景色 40 (黑) = 暗像素 → True
    - 背景色 47 (白) = 亮像素 → False

    每个像素输出为 2 个空格 + 一组 ANSI 转义前缀。
    """
    matrix: list[list[bool]] = []
    for line in terminal_str.splitlines():
        if not line.strip():
            continue
        row: list[bool] = []
        bg_dark = False
        pos = 0
        while pos < len(line):
            m = _ANSI_RE.match(line, pos)
            if m:
                # 解析 CSI 参数（如 "0;37;40"），查找背景色
                codes = m.group(1).split(";")
                for code in codes:
                    c = int(code) if code.isdigit() else 0
                    if c == 40:
                        bg_dark = True
                    elif 41 <= c <= 47 or c == 49 or c == 0:
                        bg_dark = c == 40  # reset 或其他背景色 → 非暗
                pos = m.end()
            elif line[pos] == " ":
                row.append(bg_dark)
                pos += 1
            else:
                pos += 1
        # 每 2 个空格代表 1 个像素 → 去重合并
        pixel_row = row[::2] if row else row
        if pixel_row:
            matrix.append(pixel_row)
    return matrix


def _compress_qr(terminal_str: str) -> str:
    """将二维码终端输出压缩为紧凑的 Unicode 半块字符。

    先将 ANSI 彩色输出解析为布尔矩阵，再用 Unicode 半块字符
    将每 2 行合并为 1 行：
    █ = 上暗+下暗, ▀ = 上暗+下亮, ▄ = 上亮+下暗, ' ' = 上亮+下亮
    """
    matrix = _ansi_to_matrix(terminal_str)
    if not matrix:
        # 非 ANSI 输出（如纯 ASCII），回退为简单处理
        return _compress_qr_plain(terminal_str)

    result: list[str] = []
    for i in range(0, len(matrix), 2):
        top = matrix[i]
        bot = matrix[i + 1] if i + 1 < len(matrix) else []
        compressed: list[str] = []
        width = max(len(top), len(bot))
        for j in range(width):
            td = top[j] if j < len(top) else False
            bd = bot[j] if j < len(bot) else False
            if td and bd:
                compressed.append("█")
            elif td:
                compressed.append("▀")
            elif bd:
                compressed.append("▄")
            else:
                compressed.append(" ")
        result.append("".join(compressed))
    return "\n".join(result)


def _compress_qr_plain(terminal_str: str) -> str:
    """纯文本 QR 输出的压缩（无 ANSI 转义）。"""
    lines = terminal_str.splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return terminal_str

    result: list[str] = []
    for i in range(0, len(lines), 2):
        top = lines[i]
        bot = lines[i + 1] if i + 1 < len(lines) else ""
        compressed: list[str] = []
        max_len = max(len(top), len(bot))
        for j in range(0, max_len, 2):
            tc = top[j] if j < len(top) else " "
            bc = bot[j] if j < len(bot) else " "
            td = tc not in (" ", "\t")
            bd = bc not in (" ", "\t")
            if td and bd:
                compressed.append("█")
            elif td:
                compressed.append("▀")
            elif bd:
                compressed.append("▄")
            else:
                compressed.append(" ")
        result.append("".join(compressed))
    return "\n".join(result)


# 二维码约 3 分钟过期，每 2 秒轮询一次状态
_POLL_INTERVAL = 2.0
_MAX_RETRIES = 3  # 过期后最多重新生成 3 次


async def qrcode_login() -> "Credential":
    """交互式扫码登录，返回包含有效凭据的 Credential 对象。

    流程：
    1. 生成二维码（终端 ASCII + PNG 文件）
    2. 轮询登录状态，直到用户扫码确认
    3. 二维码过期自动重新生成（最多 ``_MAX_RETRIES`` 次）

    Raises:
        RuntimeError: 超过最大重试次数仍未完成登录。
    """
    from bilibili_api.login_v2 import (
        QrCodeLogin,
        QrCodeLoginChannel,
        QrCodeLoginEvents,
    )

    for attempt in range(1, _MAX_RETRIES + 1):
        qr = QrCodeLogin(QrCodeLoginChannel.WEB)
        await qr.generate_qrcode()

        # 保存 PNG 到临时文件
        png_path = os.path.join(tempfile.gettempdir(), "ncatbot_bilibili_qr.png")
        pic = qr.get_qrcode_picture()
        if pic is not None and pic.content:
            with open(png_path, "wb") as f:
                f.write(pic.content)
            LOG.info("二维码图片已保存: %s", png_path)

        # 终端 ASCII 打印（压缩为 1/2 大小）
        terminal_str = _compress_qr(qr.get_qrcode_terminal())
        print("\n" + "=" * 50)
        print(f"  Bilibili 扫码登录 (第 {attempt}/{_MAX_RETRIES} 次)")
        print("=" * 50)
        print(terminal_str)
        print(f"  二维码图片: {png_path}")
        print("  请使用 Bilibili APP 扫描上方二维码")
        print("=" * 50 + "\n")

        # 轮询状态
        while True:
            await asyncio.sleep(_POLL_INTERVAL)
            state = await qr.check_state()

            if state == QrCodeLoginEvents.DONE:
                LOG.info("Bilibili 扫码登录成功")
                return qr.get_credential()
            elif state == QrCodeLoginEvents.CONF:
                LOG.info("已扫码，等待确认...")
            elif state == QrCodeLoginEvents.TIMEOUT:
                LOG.warning("二维码已过期")
                break  # 跳出内层循环，重新生成
            # SCAN 状态 → 继续等待

    raise RuntimeError(f"Bilibili 扫码登录失败: 已超过最大重试次数 ({_MAX_RETRIES})")
