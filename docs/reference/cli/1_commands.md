# CLI 命令签名与参数

> 全部 `ncatbot` CLI 命令、子命令及其选项/参数速查。

## 顶层命令

```
ncatbot [OPTIONS] [COMMAND]
```

| 选项 | 说明 |
|------|------|
| `--version` | 显示版本号 |
| `--help` | 显示帮助信息 |

无子命令时进入交互模式（REPL）。

## init

```
ncatbot init [OPTIONS]
```

初始化项目，创建 `config.yaml` 和 `plugins/` 目录。

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--dir` | `str` | `.` | 目标目录 |

交互式提示：

| 提示 | 说明 |
|------|------|
| 请输入机器人 QQ 号 | 写入 `bot_uin` |
| 请输入管理员 QQ 号 | 写入 `root` |

若 `config.yaml` 已存在，提示是否覆盖。

## run

```
ncatbot run [OPTIONS]
```

启动 NcatBot（连接 NapCat + 加载插件 + 监听事件）。

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--debug` | flag | `False` | 启用调试模式 |
| `--no-hot-reload` | flag | `False` | 禁用插件热重载 |
| `--plugin-dir` | `str` | `plugins` | 插件目录路径 |

## dev

```
ncatbot dev [OPTIONS]
```

以开发模式启动（`debug=True` + 热重载）。

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--plugin-dir` | `str` | `plugins` | 插件目录路径 |

## config

```
ncatbot config COMMAND
```

配置管理命令组。

### config show

```
ncatbot config show
```

以 YAML 格式显示当前全部配置。

### config get

```
ncatbot config get CONFIG_KEY
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `CONFIG_KEY` | `str` | 配置项路径，支持点分（如 `napcat.ws_uri`） |

### config set

```
ncatbot config set CONFIG_KEY CONFIG_VALUE
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `CONFIG_KEY` | `str` | 配置项路径，支持点分 |
| `CONFIG_VALUE` | `str` | 值（自动类型转换） |

类型转换规则：

| 输入值 | 转换类型 |
|--------|----------|
| `true` / `yes` | `bool (True)` |
| `false` / `no` | `bool (False)` |
| 纯数字字符串 | `int` |
| `[...]` JSON 格式 | `list` |
| 其它 | `str` |

### config check

```
ncatbot config check
```

检查配置安全性和必填项，输出问题列表。

## plugin

```
ncatbot plugin COMMAND
```

插件管理命令组。

### plugin list

```
ncatbot plugin list
```

列出已安装插件，显示名称、版本、作者、状态。读取每个插件目录下的 `manifest.toml`。

### plugin create

```
ncatbot plugin create NAME
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `NAME` | `str` | 插件名（字母开头，仅字母/数字/下划线） |

在插件目录下生成标准脚手架，包含 `__init__.py`、`manifest.toml`、`plugin.py`、`README.md`。

### plugin info

```
ncatbot plugin info NAME
```

| 参数 | 类型 | 说明 |
|------|------|------|
| `NAME` | `str` | 插件名 |

显示插件 `manifest.toml` 元数据。

### plugin enable

```
ncatbot plugin enable NAME
```

启用插件：从黑名单移除，若白名单存在则加入白名单。

### plugin disable

```
ncatbot plugin disable NAME
```

禁用插件：从白名单移除，加入黑名单。

### plugin remove

```
ncatbot plugin remove NAME
```

删除插件目录（带确认提示）。

### plugin on

```
ncatbot plugin on
```

全局开启插件加载（`plugin.load_plugin = True`）。

### plugin off

```
ncatbot plugin off
```

全局关闭插件加载（`plugin.load_plugin = False`）。

## napcat

```
ncatbot napcat COMMAND
```

NapCat 管理命令组。

### napcat diagnose

```
ncatbot napcat diagnose [COMMAND]
```

无子命令时运行完整诊断。

### napcat diagnose ws

```
ncatbot napcat diagnose ws [OPTIONS]
```

检测 NapCat WebSocket 连接。

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--uri` | `str` | 读取配置 | WebSocket URI |
| `--token` | `str` | 读取配置 | WebSocket Token |

### napcat diagnose webui

```
ncatbot napcat diagnose webui [OPTIONS]
```

检测 NapCat WebUI 状态。

| 选项 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `--uri` | `str` | 读取配置 | WebUI URI |
| `--token` | `str` | 读取配置 | WebUI Token |

## 源码结构

```
ncatbot/cli/
├── __init__.py          # 导出 main
├── __main__.py          # python -m ncatbot.cli 入口
├── main.py              # Click root group
├── commands/
│   ├── init.py          # init 命令
│   ├── run.py           # run / dev 命令
│   ├── config.py        # config 命令组
│   ├── plugin.py        # plugin 命令组
│   └── napcat.py        # napcat 命令组
├── utils/
│   ├── colors.py        # 语义化颜色输出
│   └── repl.py          # 交互式 REPL 引擎
└── templates/plugin/    # 插件脚手架模板
```
