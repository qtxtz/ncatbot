# CLI 命令参考

> `ncatbot` 命令行工具完整 API 参考。基于 [Click](https://click.palletsprojects.com/) 构建。

## Quick Start

```bash
ncatbot --help          # 查看所有命令
ncatbot <command> --help  # 查看单个命令帮助
```

## 文档清单

| 文件 | 说明 |
|------|------|
| [1_commands.md](1_commands.md) | 全部命令签名与参数 |

## 入口点

```toml
# pyproject.toml
[project.scripts]
ncatbot = "ncatbot.cli:main"
```

也可通过模块方式调用：

```bash
python -m ncatbot.cli
```
