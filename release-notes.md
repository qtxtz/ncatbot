## ✨ 新功能
- **adapter/github**: 网络代理与镜像支持 — GitHub 适配器新增 `network_mode`（proxy / mirror / direct）、`mirror_url`、`mirror_hosts` 配置项，GitHubBotAPI 支持代理转发 (16566db)
- **bilibili**: 新增视频解析接口 (ab8cc65)

## 🐛 修复
- **cli**: `ref` 命令增加 GitHub API fallback 机制 — API 限流时自动通过 releases/latest 重定向获取最新 tag 并直接下载 (3a3d6c1)

## ♻️ 重构
- **plugin**: ConfigMixin 双层配置模型重写 — 插件源码目录 `config.yaml` 为低优先级默认值，全局 `config.yaml` 的 `plugin.plugin_configs.<name>` 为高优先级覆盖；新增 `init_defaults()` 补充内存默认值（不持久化）；`set_config()` / `update_config()` 即时持久化到全局 config；`PluginManifest.plugins_dir` 重命名为 `plugin_path` (3949b19)

## 📝 文档
- 同步 ConfigMixin 双层配置模型文档：guide/配置与数据、reference/基类 + Mixins、Skill 参考文件 (c349e8d)
