## ✨ 新功能
- **lark**: 新增飞书适配器实现 (e8b0c04c)
- **dispatch-filter**: 新增分发过滤服务 — DispatchFilterService 按 group/user 维度管理过滤规则；DispatchFilterHook 全局拦截匹配事件分发；DispatchFilterMixin 插件便捷 API；SystemManager 新增管理命令 (79cdda1f)

## ♻️ 重构
- **napcat**: 重构 Linux NapCat 启动检测逻辑 — 多策略检测 (napcat CLI / screen / pgrep)、rootless 安装路径支持、启动方式分层回退 (49f48467)

## ✅ 测试
- **lark**: 新增飞书适配器单元测试 (5c60738b)
- **dispatch-filter**: 新增 18 个测试 (14 unit + 4 integration) (79cdda1f)

## 📝 文档
- 更新分发过滤服务相关文档与 skills (e157949e)
- 补充飞书适配器相关 skills (5367ed97)
