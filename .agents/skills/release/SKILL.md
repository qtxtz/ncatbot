---
name: release
description: "发布 NcatBot 新版本到 PyPI 和 GitHub Release，或仅编排 Commit 推送到 main。从工作区变更编排 commit 到最终发布的全链路流程。Use when: 发版、release、发布、changelog、版本号、pick commits、挑选提交、release notes、编排 commit、push、推送。"
license: MIT
---

# 技能指令

你是 NcatBot 发布助手。帮助用户完成从 **工作区变更到版本发布** 的全链路流程。

## 模式选择

根据变更内容自动判断模式，或由用户指定：

| 模式 | 触发条件 | 流程 |
|------|---------|------|
| **发布模式** | 变更涉及 `ncatbot/`、`pyproject.toml` 等核心代码 | 全链路：Commit → 版本号 → 构建 → PyPI → GitHub Release |
| **推送模式** | 仅涉及 docs、examples、skills、tests 等非核心文件 | Commit → Push → 可选更新 Release Asset |

**自动判断规则**：检查工作区变更 + 待推送 commit 中是否包含以下路径：
- `ncatbot/` — 核心框架代码
- `pyproject.toml` — 项目配置/依赖
- `main.py` — 入口

若上述路径 **均未变更**，自动进入推送模式；否则进入发布模式。拿不准时用 `vscode_askQuestions` 询问用户。

## 前置条件

- Python 虚拟环境已激活（`.venv\Scripts\activate.ps1`）
- 已安装 `build` 和 `twine`（`uv pip install build twine`）
- PyPI API Token 已配置为环境变量 `TWINE_PASSWORD`（见 `.vscode/settings.json`）
- GitHub CLI（`gh`）已登录（`gh auth login --web`）

## 发布模式：全链路流程总览

```
工作区变更审查 → Commit 编排 → 已有 Commit 审查 → 版本号确定 → Release Notes → 构建 → PyPI → 参考资料打包 → GitHub Release → 清理
```

---

### 阶段 1：工作区变更审查与 Commit 编排

目标：将工作区中未提交的变更组织为规范的 conventional-commits。

#### 1.1 收集工作区状态

```powershell
git status --short
git diff --stat
```

#### 1.2 ASK：哪些变更纳入本次发布

使用 `vscode_askQuestions` 工具展示变更文件列表，让用户决定：

- 哪些文件/改动需要纳入本次发布
- 哪些改动暂不提交（留到后续版本）

> **决策点**：如果工作区干净（无未提交变更），跳过此阶段直接进入阶段 2。

#### 1.3 ASK：如何分组为 Commits

将用户选中的变更按逻辑分组，提出建议分组方案后 **用 `vscode_askQuestions` 确认**：

- 建议按模块/功能拆分为多个 commit
- 每个 commit 建议 conventional-commits 格式的 message（`type(scope): description`）
- 用户可以合并、拆分、或调整分组

#### 1.4 执行 Commit

按用户确认的分组方案依次执行：

```powershell
git add <files>
git commit -m "type(scope): description"
```

重复直到所有选中的变更都已提交。

---

### 阶段 2：已有 Commit 审查

> 详细参考：[references/commit-picking.md](references/commit-picking.md)

目标：审查自上一个 tag 以来的所有 commits，确认哪些纳入 release notes。

#### 2.1 获取候选 Commits

```powershell
$lastTag = git describe --tags --abbrev=0 2>$null
if (!$lastTag) { $lastTag = (git rev-list --max-parents=0 HEAD) }
git log "$lastTag..HEAD" --oneline --no-merges
```

#### 2.2 分类展示

按 conventional-commits 类型分组：

| 类别 | 前缀 | Emoji | 默认纳入 |
|------|-------|-------|---------|
| 新功能 | `feat` | ✨ | ✅ |
| 修复 | `fix` | 🐛 | ✅ |
| 重构 | `refactor` | ♻️ | ✅ |
| 性能优化 | `perf` | ⚡ | ✅ |
| 破坏性变更 | 含 `BREAKING CHANGE` 或 `!` | 💥 | ✅ |
| 文档 | `docs` | 📝 | ❌ |
| 测试 | `test` | ✅ | ❌ |
| 构建/依赖 | `chore`, `build`, `ci` | 🔧 | ❌ |

#### 2.3 ASK：确认纳入范围

使用 `vscode_askQuestions` 让用户确认：
- 默认纳入的类别是否需要排除某些 commit
- 默认跳过的类别是否需要额外纳入某些 commit

---

### 阶段 3：版本号确定

> 详细参考：[references/release-steps.md](references/release-steps.md)

#### 版本号递增规则

版本格式：`X.Y.Z[.postN]`

| 条件 | 版本递增 | 示例 | 是否 ASK |
|------|---------|------|--------|
| 仅 1 个 `fix`，紧急热修复 | **post** | 5.1.0 → 5.1.0.post1 | 自动 |
| 多个 `fix` 或小的 `feat` 增加 | **patch** | 5.1.0 → 5.1.1 | 自动 |
| 大型 `feat` 或破坏性变更 | **minor** | 5.1.0 → 5.2.0 | 自动 |
| 无法归类（如仅 refactor/docs） | — | — | **必须 ASK** |

> **major 版本不在 AI 决策范围内**。major 升版只由人类主动发起，AI 不主动提及、不建议、不询问。如果用户明确说「升 major」，再按用户指示执行。

**判断优先级**（自上而下，第一条匹配则停止）：
1. 仅 1 个 commit 且类型为 `fix` → **post**
2. 全部为 `fix`（多个）或存在小 `feat` → **patch**
3. 存在大型 `feat`（新模块/重要功能）或 `BREAKING CHANGE` → **minor**
4. 以上无法判断 → 用 `vscode_askQuestions` 询问用户

#### 执行版本号更新

读取 `pyproject.toml` 当前版本，计算新版本号后直接修改。

---

### 阶段 4：生成 Release Notes

基于阶段 2 确认的 commits 生成 `release-notes.md`：

```markdown
## ✨ 新功能
- **scope**: 描述 (hash)

## 🐛 修复
- 描述 (hash)

## ♻️ 重构
- 描述 (hash)

## 💥 破坏性变更
- 描述 (hash)
```

格式化规则：
- 移除 commit message 的 `type(scope):` 前缀，只保留描述
- scope 非空时加粗标注：`- **scope**: 描述 (hash)`
- 空类别不展示
- 破坏性变更始终排在最前

生成后 **展示给用户审阅**，如有修改意见通过 `vscode_askQuestions` 收集。

---

### 阶段 5：构建发行包

```powershell
if (Test-Path dist) { Remove-Item dist -Recurse -Force }
python -m build
```

构建产物：
- `dist/ncatbot5-{version}-py3-none-any.whl`
- `dist/ncatbot5-{version}.tar.gz`

---

### 阶段 6：发布到 PyPI

```powershell
python -m twine upload dist/* -u __token__
```

`twine` 自动读取 `TWINE_PASSWORD` 环境变量中的 API Token。

---

### 阶段 7：打包用户参考资料

将 `examples/`、`.agents/skills/`、`docs/` 打包为 zip（排除 `__pycache__`）：

```powershell
$ver = "X.Y.Z"  # 替换为实际版本
$zipPath = "dist\ncatbot5-$ver-user-reference.zip"
$tempDir = "dist\_pack_temp"

$files = Get-ChildItem -Recurse examples, .agents\skills, docs -File |
    Where-Object { $_.FullName -notmatch '__pycache__' }

if (Test-Path $tempDir) { Remove-Item $tempDir -Recurse -Force }
foreach ($f in $files) {
    $rel = $f.FullName.Replace((Get-Location).Path + '\', '')
    $dest = Join-Path $tempDir $rel
    $destDir = Split-Path $dest
    if (!(Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
    Copy-Item $f.FullName $dest
}
Compress-Archive -Path "$tempDir\*" -DestinationPath $zipPath
Remove-Item $tempDir -Recurse -Force
```

---

### 阶段 8：创建 GitHub Release

```powershell
$ver = "X.Y.Z"
gh release create "v$ver" `
    "dist/ncatbot5-$ver-user-reference.zip" `
    "dist/ncatbot5-$ver-py3-none-any.whl" `
    "dist/ncatbot5-$ver.tar.gz" `
    --title "v$ver" `
    --notes-file release-notes.md `
    --repo ncatbot/NcatBot
```

---

### 阶段 9：清理与收尾

发布完成后执行：

```powershell
Remove-Item release-notes.md -ErrorAction SilentlyContinue
```

并向用户确认发布结果。

---

## 推送模式：仅 Commit & Push（不发新版本）

适用于与核心代码无关的变更（docs、examples、skills、tests、dev 脚本等）。

### 流程

```
工作区变更审查 → Commit 编排 → Push → （可选）更新 Release Asset
```

### P1：工作区变更审查与 Commit 编排

与发布模式的阶段 1 **完全相同**（1.1 ~ 1.4），参照上文。

### P2：推送到 main

```powershell
git push origin main
```

### P3：判断是否需要更新 Release Asset

如果本次推送的 commit 涉及以下路径，需要重新打包并替换最新 Release 中的 `user-reference.zip`：

- `docs/`
- `examples/`
- `.agents/skills/`

**自动判断**：检查本次推送的 commit 是否包含上述路径的文件变更：

```powershell
$lastTag = git describe --tags --abbrev=0 2>$null
git diff --name-only "$lastTag..HEAD" | Select-String "^(docs/|examples/|\.agents/skills/)"
```

若匹配到文件 → 执行 P4；否则流程结束。

### P4：重新打包并替换 Release Asset

#### 4a. 获取最新 Release tag

```powershell
$latestTag = git describe --tags --abbrev=0
$ver = $latestTag -replace '^v', ''
```

#### 4b. 打包参考资料（同发布模式阶段 7）

```powershell
$zipPath = "dist\ncatbot5-$ver-user-reference.zip"
$tempDir = "dist\_pack_temp"

if (Test-Path dist) { Remove-Item dist -Recurse -Force }

$files = Get-ChildItem -Recurse examples, .agents\skills, docs -File |
    Where-Object { $_.FullName -notmatch '__pycache__' }

New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
foreach ($f in $files) {
    $rel = $f.FullName.Replace((Get-Location).Path + '\', '')
    $dest = Join-Path $tempDir $rel
    $destDir = Split-Path $dest
    if (!(Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
    Copy-Item $f.FullName $dest
}
Compress-Archive -Path "$tempDir\*" -DestinationPath $zipPath
Remove-Item $tempDir -Recurse -Force
```

#### 4c. 替换 Release 中的旧 asset

```powershell
# 删除旧的 user-reference.zip
gh release delete-asset "v$ver" "ncatbot5-$ver-user-reference.zip" --repo ncatbot/NcatBot --yes

# 上传新的
gh release upload "v$ver" $zipPath --repo ncatbot/NcatBot
```

#### 4d. 清理

```powershell
if (Test-Path dist) { Remove-Item dist -Recurse -Force }
```

---

## ASK 决策点汇总

以下场景 **必须** 使用 `vscode_askQuestions` 工具向用户确认：

| 阶段 | 决策点 | 说明 |
|------|--------|------|
| 模式选择 | 发布 or 推送 | 变更范围无法自动判断时询问 |
| 1.2 / P1 | 哪些变更纳入 | 展示 `git status` 文件列表让用户勾选 |
| 1.3 / P1 | Commit 分组方案 | 提出分组建议让用户确认/调整 |
| 2.3 | Commit 纳入范围 | 让用户确认哪些已有 commit 进 release notes（仅发布模式） |
| 3 | 版本号（无法自动判断时） | 变更类型不明时询问；major 由人类主动发起，AI 不涉及 |
| 4 | Release Notes 内容 | 展示生成的 notes 让用户审阅和修改（仅发布模式） |

以下场景 **自动执行**，不需要询问：

| 场景 | 自动行为 |
|------|---------|
| 工作区无未提交变更 | 跳过 Commit 编排 |
| 变更仅涉及非核心文件 | 自动进入推送模式 |
| 推送后 commit 涉及 docs/examples/skills | 自动更新 Release Asset |
| 推送后 commit 不涉及上述路径 | 流程结束，不更新 Asset |
| 仅 1 个 fix | post 版本 |
| 多个 fix 或小 feat | patch 版本 |
| 大型 feat 或 BREAKING CHANGE | minor 版本 |
| 构建、上传、打包 | 依次自动执行 |

## 关键约束

- **先挑选 commit，再定版本号** — 版本号取决于本次包含的变更类型
- 构建前必须清理旧 `dist/` 目录
- 打包参考资料时排除 `__pycache__` 目录
- PyPI Token **不要** 提交到版本控制
- `release-notes.md` 是临时文件，发布完成后删除
