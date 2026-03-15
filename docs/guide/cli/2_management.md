# 插件与配置管理

> 一句话：用 `ncatbot plugin` 管理插件的创建、启用、禁用，用 `ncatbot config` 查看和修改配置，用 `ncatbot napcat diagnose` 排查连接问题。

## 前提条件

- 已完成 [项目初始化与启动](1_getting_started.md)

## 插件管理

### 查看已安装插件

```bash
ncatbot plugin list
```

输出示例：

```
已安装插件:
  插件加载: 开启

  HelloWorld v0.1.0 by Author  [启用]
    打招呼插件
  MyPlugin v1.0.0 by Alice     [禁用]
    功能插件
```

状态说明：

| 状态 | 含义 |
|------|------|
| 启用 | 正常加载 |
| 禁用 | 在黑名单中，不会加载 |
| 未在白名单 | 白名单已配置，但该插件不在其中 |

### 创建插件脚手架

```bash
ncatbot plugin create my_plugin
```

自动在 `plugins/` 下生成标准目录结构：

```
plugins/my_plugin/
├── __init__.py
├── manifest.toml
├── plugin.py
└── README.md
```

插件名规则：以字母开头，只能包含字母、数字和下划线。

### 查看插件详情

```bash
ncatbot plugin info my_plugin
```

显示 `manifest.toml` 中的元数据：版本、作者、描述、入口文件、依赖等。

### 启用 / 禁用插件

```bash
# 启用单个插件
ncatbot plugin enable my_plugin

# 禁用单个插件
ncatbot plugin disable my_plugin

# 全局开启插件加载
ncatbot plugin on

# 全局关闭插件加载
ncatbot plugin off
```

### 删除插件

```bash
ncatbot plugin remove my_plugin
```

会弹出确认提示，确认后删除整个插件目录。

## 配置管理

### 查看当前配置

```bash
ncatbot config show
```

以 YAML 格式输出全部配置项。

### 读取配置项

```bash
ncatbot config get napcat.ws_uri
```

支持点分路径访问嵌套配置。

### 设置配置项

```bash
ncatbot config set napcat.ws_uri "ws://localhost:3001"
ncatbot config set debug true
ncatbot config set plugin.plugin_blacklist '["PluginA", "PluginB"]'
```

值类型自动转换规则：

| 输入 | 转换结果 |
|------|----------|
| `true` / `yes` | `True`（布尔） |
| `false` / `no` | `False`（布尔） |
| 纯数字 | `int` |
| `[...]` JSON 数组 | `list` |
| 其它 | `str` |

### 检查配置

```bash
ncatbot config check
```

检查安全性问题和必填项，输出问题列表或通过提示。

## NapCat 诊断

### 完整诊断

```bash
ncatbot napcat diagnose
```

一键运行所有诊断项。

### WebSocket 连接检测

```bash
ncatbot napcat diagnose ws
```

可选参数：

| 选项 | 说明 |
|------|------|
| `--uri <地址>` | 指定 WebSocket URI（默认读取配置） |
| `--token <令牌>` | 指定 WebSocket Token（默认读取配置） |

### WebUI 状态检测

```bash
ncatbot napcat diagnose webui
```

可选参数：

| 选项 | 说明 |
|------|------|
| `--uri <地址>` | 指定 WebUI URI（默认读取配置） |
| `--token <令牌>` | 指定 WebUI Token（默认读取配置） |

## 延伸阅读

- [项目初始化与启动](1_getting_started.md) — init / run / dev 命令详解
- [配置管理指南](../configuration/) — config.yaml 字段详解
- [插件开发指南](../plugin/) — 插件开发完整教程
- [CLI 命令参考](../../reference/cli/) — 全部命令签名速查
