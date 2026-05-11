"""SnowLuma 启动编排子模块（platform / installer / launcher）。

设计与 ``ncatbot.adapter.napcat.setup`` 对标，但完全独立：

- ``platform``：平台抽象（目前仅 Windows，预留 Linux/macOS 接口）
- ``installer``：从 GitHub Releases 下载并解压 ``SnowLuma-vX.Y.Z-win-x64.zip``
- ``launcher``：双模式启动编排（skip_setup 直连 / 自动安装+启动）
"""
