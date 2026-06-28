# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

Python 3.10+ 工具，用于压缩解压 ZIP、RAR、7z 格式。CLI 基于 typer，Core 层与前端解耦，可挂载 GUI。

## 技术栈
- Python 3.10+
- CLI: typer
- GUI: CustomTkinter + tkinterdnd2（可选）
- ZIP: zipfile (stdlib)
- RAR 解压: rarfile + unrar.exe (bin/unrar.exe)
- 7z: py7zr
- 打包: pyinstaller
- 测试: pytest

## Commands

```bash
.venv\Scripts\activate              # 激活虚拟环境（Windows）
.venv\Scripts\python.exe -m pip install -e .  # 安装项目到 venv
pytest tests/ -v                    # 运行测试
python -m zip_rar_tool --help       # 查看 CLI 帮助
```

> **注意**：本项目必须使用虚拟环境 `.venv/`。`.venv/` 已加入 `.gitignore`，不要提交到仓库。

## 项目结构

```
zip_rar_tool/              # 库代码（可 import）
  __init__.py              # 暴露 extract, list_files, compress
  __main__.py              # python -m zip_rar_tool 入口
  cli.py                   # typer CLI 定义
  core.py                  # ArchiveHandler 统一调度
  backends/                # 策略模式，每个格式一个文件
    __init__.py
    zip_backend.py         # 基于 zipfile
    rar_backend.py         # 基于 rarfile + unrar.exe
    sevenz_backend.py      # 基于 py7zr
  utils.py                 # 编码处理、路径工具
gui/                       # GUI 前端（CustomTkinter）
  __init__.py
  app.py                   # 主窗口 + 顶部 Tab（解压/压缩/查看）
  widgets/                 # Tab 面板 + 公共组件
bin/unrar.exe              # 免费可分发，直接入库
```

## 关键约定
- **RAR 压缩**：仅检测到系统 WinRAR 时可选提供（读注册表），不强依赖
- **中文编码**：RAR 需处理 CP936，ZIP 是 UTF-8
- **压缩策略**：优先 .zip，次选 .7z。RAR 压缩是可选降级
- **自动调度**：core.py 根据文件后缀自动选派对应 backend
- **Core 与前端解耦**：`core.extract/compress/list_files` 是纯函数，CLI 和 GUI 都是薄调用层

---

## 开发工作流

核心原则: **实现 A 功能，绝不破坏 B 功能。** 流程按任务类型分两轨。

### 任务分类

| 类型 | 特征 | 示例 |
|------|------|------|
| **Feature** | 新功能、跨模块改动、架构调整 | 添加 GUI 界面、新增格式支持、重构 backend 接口 |
| **Bug Fix** | 修复缺陷、单文件小改、样式修正 | 修复 RAR 编码错乱、修正进度条卡顿 |

判断标准: 改动涉及 >2 个源文件 或 新增行为定义 → Feature；否则 → Bug Fix。

**"已完成"的判定标准**：不可凭"代码看起来对"就宣布完成。必须提供**测试命令 + 输出**作为证据。
- Bug 修复 → 功能测试命令 + 输出证明 bug 不复现
- UI 改动 → 模拟点击测试命令 + 输出证明交互正确
- pytest → 粘贴 `XX passed` 输出
- 证据不足 → 回到修复步骤，不可跳过

---

### Feature 轨道

| # | 步骤 | 技能 | 产出 |
|---|------|------|------|
| 1 | 需求澄清 | `mattpocock-skills-grilling` | 明确的需求边界和验收标准 |
| 2 | 领域建模 + **设计探针** | `mattpocock-skills-domain-modeling` + 探针验证（见下） | CONTEXT.md + API 存在性验证 |
| 3 | 制定计划 | `superpowers-skills-writing-plans` | `docs/plans/YYYY-MM-DD-<feature>.md` |
| 4 | **人工审查** | — | 用户批准计划 |
| 5 | TDD 实现 | `mattpocock-skills-tdd` + `superpowers-skills-test-driven-development` + `superpowers-skills-subagent-driven-development` | 测试先行，逐任务实现 |
| 6 | 功能测试 | CustomTkinter 功能测试 + **模拟点击测试**（不可跳过） | 功能/事件链验证通过 |
| 7 | 代码审查 | `mattpocock-skills-review`（见代码审查清单） | 审查通过 |
| 8 | 回归测试 | `pytest tests/` | 全部绿色，旧功能无退化 |
| 9 | 归档 + 版本 | git commit + 更新 Version.md | 版本锚点，知识库更新 |
| 10 | **元学习** | 十问分析本次教训 → 规则自检（见"每次 Debug 后必须执行"） | CLAUDE.md 持续进化 |

---

### 🔴 Feature Step 2 — 设计探针（领域建模后的代码验证）

领域建模完成后、制定计划前，对设计中涉及的 API、集成点、边界条件写 5-10 行探针脚本。**不等实现阶段才发现 API 不存在。**

| 探针类型 | 验证问题 | 示例 |
|---------|---------|------|
| API 存在性 | 要调的方法真的存在？ | `hasattr(ctk.CTkTabview, 'add')` → 确认 API |
| 集成点兼容 | 两个模块的接口真的匹配？ | `core.extract()` 返回类型 GUI 能否消费？ |
| 边界条件 | 空值/溢出/极端输入？ | 文件数为 0 或 1000 时 UI 行为正确？ |
| 失败预演 | "如果方案失败，最先在哪崩？" | 主动验证那个点，不等崩溃才排查 |

探针脚本格式：
```python
# 5 行探针：验证关键 API 在运行时真实存在
import customtkinter as ctk
app = ctk.CTk()
bar = ctk.CTkProgressBar(app)
bar.set(0.5)
assert hasattr(bar, 'set'), "CTkProgressBar.set API 不存在，需替换方案"
```

**硬规则**：
- 设计涉及不熟悉的 API → **必须写探针**
- 两个模块首次对接 → **必须写集成探针**
- 探针通过 → 进入 Step 3 制定计划
- 探针失败 → 修正设计，**不带着错误假设进入编码**

---

### Bug Fix 轨道

| # | 步骤 | 技能 | 产出 |
|---|------|------|------|
| 1 | 需求界定 | `mattpocock-skills-grilling` | 精确问题现象和边界 |
| 2 | **诊断根因** | 🔴 三 skill 联合调用（见下） | 根因确认 + DEBUG.md |
| 3 | 制定计划 | `superpowers-skills-writing-plans` | 修复计划 |
| 4 | **人工审查** | — | 用户批准 |
| 5 | TDD 修复 | `mattpocock-skills-tdd` + `superpowers-skills-test-driven-development` | 先写复现测试 → 失败 → 修复 → 通过 |
| 6 | 功能测试 | CustomTkinter 功能测试 + **模拟点击测试**（不可跳过，改动 ≥1 行即执行） | 功能验证 + 事件链验证 |
| 7 | 代码审查 | `mattpocock-skills-review`（见代码审查清单） | 审查通过 |
| 8 | 回归测试 | `pytest tests/` | 全部绿色 |
| 9 | 归档 + 版本 | git commit + 更新 Version.md | 版本锚点 |
| 10 | **元学习** | 十问分析本次教训 → 规则自检 | CLAUDE.md 持续进化 |

**🔴 Bug Fix Step 2 — 诊断根因（三 skill 联合调用，不可跳过）**

进入 Step 2 **立即按顺序调用**以下三个 skills，不等失败：

| 顺序 | Skill | 核心作用 |
|------|-------|---------|
| 1 | `Shen_Huang_debugging_skill_auto_research` | Anti-Bulldozer：Observe→Hypothesize→Experiment→Conclude，写入 DEBUG.md，每实验 ≤5 行 |
| 2 | `mattpocock-skills-diagnosing-bugs` | Phase 1：建 feedback loop——一个能复现 bug 的自动化命令 |
| 3 | `my-systematic-debugging` + `superpowers-skills-systematic-debugging` | 反转假设 + 隔离测试 + 十问根因分析 + Iron Law |

**诊断必须包含修复方案副作用分析**：
- 改动会触达哪些机制？（backend/thread/callback/UI/widget）
- 这些机制之间有哪些耦合点？
- 如果修复方案失败，最可能的副作用是什么？→ 写测试验证这个点

---

### 十问根因分析法（n-why，不限于 10 问）

**原则**：不停追问"为什么"，直到触及**系统性问题**（流程/规则/机制缺陷），而非停留在**个人失误**（"我忘了/我看错了"）。

**终止条件**：根因达到以下任一层次即可停止。
- ✅ 规则缺失（CLAUDE.md 没有覆盖这个场景）
- ✅ 流程缺陷（某个步骤缺少检查点）
- ✅ 技能缺陷（缺少特定的 skill 调用）
- ✅ 类别抽象不足（规则写得太具体，没覆盖同类问题）
- ❌ 个人失误（"我忘了/看错了"→ 不是根因，继续往下问）

**格式**：
```
第一问：为什么 [现象]？
答：[直接原因]

第二问：为什么 [上一答案]？
答：[更深原因]

...继续直到触达系统性问题...

第 N 问：为什么 [上一答案]？
答：[系统性根因]
→ 对策：[修改 CLAUDE.md / 增加检查点 / 更新规则]
```

### 每次 Debug 后必须执行

修复提交后，执行以下三步：

1. **十问分析**：追问直到触达系统性根因
2. **写入 lesson-learned**：`docs/lessons/lesson-learned-<描述>-<日期>.md`
   - 现象 → 十问链条 → 根因 → 预防对策 → 是否需修改 CLAUDE.md
3. **规则自检**：如果根因指向 CLAUDE.md 规则缺陷 → **通知用户，用户同意后修改**

### 常见错误模式及预防

| 错误模式 | 表现 | 预防 |
|---------|------|------|
| **速度偏见** | pytest 全过 → "看起来对" → 跳过功能测试 | Step 6 不可跳过，任何改动 ≥1 行必须有功能验证 |
| **"简单修复"幻觉** | 改动小 → 直觉认为不会出错 | Step 2 副作用分析——小改动也可能触发跨模块耦合 |
| **文字游戏** | "UI 改动"范围被自行缩小 | widget/layout/thread/callback/event 零容忍清单 |
| **自欺式自检** | 审查清单在脑子里跑，不贴证据 | 每项必须贴命令+输出 |

### 硬规则

- Feature Step 2（设计探针）不可跳过——不熟悉 API 不带假设编码
- Bug Fix Step 2（诊断根因）不可跳过——根源未知的修复 = 猜測修 bug
- Step 6（功能测试）不可跳过——"简单修复"不是跳过测试的理由。改动 ≥1 行就要验证
- 涉及 **widget/layout/thread/callback/event** 的改动 → **零容忍**，必须功能测试

### 代码审查清单

审查时必须逐项确认，**每一项必须附具体证据（命令 + 输出），不可自欺欺人**：

- [ ] **功能正确**：实际运行修复后的代码，验证用户报告的问题不再出现。**必须贴功能测试命令 + 输出**。代码看起来对 ≠ 功能正常。
- [ ] **反馈循环**：必须有一条命令能复现修复效果。**贴命令 + 输出**，不可写"手动测试"三个字就当过了。
- [ ] **无回归**：`pytest tests/` 全部绿色。**贴 pytest 输出最后一行**（`XX passed`）。
- [ ] **无过度修改**：`git diff --stat` 只涉及修复本身，无顺手重构。**贴 diff 文件列表**。
- [ ] **日志可查**：如涉及文件 I/O 或异常路径，日志有记录。**贴关键日志行**。
- [ ] **根因已记录**：commit message 包含根因机制，不只是"修复了 XX"。**贴 commit message**。

---

## Behavioral Guidelines

Reduce common LLM coding mistakes. Bias toward caution over speed. For trivial tasks, use judgment.

### 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them — don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

### 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- Remove only imports/variables/functions that YOUR changes made unused.

### 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

---

## 测试原则

### 技术验证 ≠ 用户体验验证

**代码通过不等于用户满意。** 单元测试验证代码行为契约，用户验证真实交互体验。两者不可互相替代。

### 关键反例

| 技术验证（Pass） | 用户体验（Fail） |
|------|------|
| `assert widget.winfo_exists()` | 用户实际看不到——被其他组件遮挡或在屏幕外 |
| `assert os.path.exists(path)` | 用户在资源管理器里找不到——路径太深 |
| `assert progress_bar.get() == 0.5` | 用户看到进度条卡在 50% 不动——后台线程阻塞 UI |

### 测试规则

- **模拟真实操作**：测试时使用鼠标点击、键盘输入等用户实际操作方式，不直接调内部方法
- **端到端验证**：每次改完代码后启动 app，亲自操作一遍完整流程
- **边界情境**：多文件、长路径名、大文件、特殊字符、密码加密等实际使用场景

### 三层测试体系

| 层级 | 何时执行 | 验证范围 | 命令 |
|------|---------|---------|------|
| **单元测试** | 每次改动后 | Python 逻辑正确性 | `pytest tests/ -v` |
| **功能测试** | UI 改动后（强制） | CustomTkinter 绘制/事件/线程实际行为 | 自定义 CTk 测试脚本 |
| **用户场景测试** | commit 前（强制） | 用户实际操作流程 | 启动 app 手动验证 |

**每种测试覆盖不同的失败模式**，不可互相替代：

| 通过 | 仍可能失败 |
|------|-----------|
| pytest 全部通过 | 线程阻塞导致 UI 卡死 |
| pytest + 功能测试 | 按钮与设计稿样式不一致 |
| 全部自动化测试 | 用户屏幕分辨率下布局错乱 |

### 测试清单

- [ ] 用鼠标（不是代码）操作完整个用户流程
- [ ] 用键盘快捷键验证（如 Tab 切换等）
- [ ] 在默认 1920×1080 分辨率下确认 UI 布局正常
- [ ] 检查状态栏/日志区提示信息是否准确、及时

---

## HOOK 保护

PreToolUse hook 仅在 `git commit` 时检查 **Version.md 是否包含当前版本号**，不一致则阻断。Write/Edit 操作不再需要计划文件门禁——行为规范由技能对话驱动，不由机械阻断保证。

---

## 日志记录规则

### 运行日志

- 每次操作将运行日志追加写入 `logs/runs/run_log_YYYY-MM-DD.txt`
- 运行日志头部必须包含版本号（如 `[START] v0.2.2`）
- NEVER delete 运行日志

### 测试日志

- 每次执行 `pytest` 后，测试结果保存到 `docs/test-logs/YYYY-MM-DD-<feature>.txt`
- 测试日志文件头部必须标注版本号（如 `# Version: v0.2.2`）
- NEVER delete 测试日志

### 日志目录

- `logs/` 目录自动创建
- 日志文件大小超过 10MB 时自动轮转（添加 `.1` 后缀）

---

## 其他规则

- 执行范围内：当前项目目录下的任何增删查改操作，**直接执行，无需询问**
- 执行范围外：任何修改当前项目以外文件的操作，必须先询问用户
- 涉及文件变更时新建版本，不覆盖原文件，更新 `Version.md`
- 每次修改完成后必须执行：`git commit` + 更新 `Version.md`
- `Version.md` 中每个版本号对应一个 `git tag`，版本与 commit 一一对应
- Version.md 顶部必须有 **版本映射表**，列出 Version / Tag / Commit / Time 的对应关系
- **Time 列必须精确到秒**（格式 `YYYY-MM-DD HH:MM:SS`，UTC+8），不可只有日期
- 每条版本条目必须标注 tag: vX.Y.Z 和 commit: <hash>，标题行含精确时间
- 版本发布时执行：git tag vX.Y.Z，并在 Version.md 中更新映射表 + 标注 tag 引用
- 版本条目按时间倒序排列（最新版本在最上面）
- 保留所有历史版本文件，不删除，便于回滚
- 提交修改到本地 git
- **每次执行任务完成后，必须在回复末尾告知用户当前版本号**
- 在任何情况下，都不要主动调用或执行 `/opsx:apply` 命令
