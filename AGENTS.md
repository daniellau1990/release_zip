# AGENTS.md

## 项目概述
Python �?+ CLI 工具，用于压�?解压 ZIP、RAR�?z 格式�?

## 技术栈
- Python 3.10+
- CLI: typer
- ZIP: zipfile (stdlib)
- RAR 解压: rarfile + unrar.exe (bin/unrar.exe)
- 7z: py7zr
- 测试: pytest

## 项目结构
```
zip_rar_tool/              �?库代码（�?import�?
  __init__.py              �?暴露 extract, list_files, compress
  __main__.py              �?python -m zip_rar_tool 入口
  cli.py                   �?typer CLI 定义
  core.py                  �?ArchiveHandler 统一调度
  backends/                �?策略模式，每个格式一个文�?
    __init__.py
    zip_backend.py         �?基于 zipfile
    rar_backend.py         �?基于 rarfile + unrar.exe
    sevenz_backend.py      �?基于 py7zr
  utils.py                 �?编码处理、路径工�?
bin/unrar.exe              �?免费可分发，直接入库
```

## 关键约定
- **RAR 压缩**：仅检测到系统 WinRAR 时可选提供（读注册表），不强依赖
- **中文编码**：RAR 需处理 CP936，ZIP �?UTF-8
- **压缩策略**：优先用 .zip �?.7z，RAR 压缩是可选降�?
- **自动调度**：core.py 根据文件后缀自动选派对应 backend

## 开发命�?
```bash
.venv\Scripts\activate           # 激活虚拟环境（Windows�?
.venv\Scripts\python.exe -m pip install -e .  # 安装项目�?venv
pytest tests/ -v                 # 运行测试
python -m zip_rar_tool --help    # 查看 CLI 帮助
```

> **注意**：本项目必须使用虚拟环境 `.venv/`。如果联网失败，运行 `cmd通过代理联网.bat` 后再执行 pip install�?
> `.venv/` 已加�?`.gitignore`，不要提交到仓库�?

## 三层防御方案（参�?Guardrail 方案设计�?

### Tier 1: AGENTS.md 结构强化（预防层�?
- 工作流和合规清单放在文件顶部，强�?AI 在写代码前阅�?
- `QUICK COMPLIANCE CHECK` 自查清单
- `opencode.json` �?`"instructions": ["AGENTS.md"]` 确保每次会话加载

### Tier 2: workflow_check.py 守卫 + OpenCode 插件（拦截层�?

**双重机制，自动拦截：**

**A. OpenCode 插件（自动）**
位于 `.opencode/plugins/workflow-guard.js`，通过 `tool.execute.before` 钩子在每�?`edit`/`write`/`apply_patch` 前自动运行检查：
- 无计划文�?�?抛出错误，阻止操�?
- AI 无法绕过，无需人工干预

**B. workflow_check.py（手�?底层�?*
位于 `.opencode/hooks/workflow_check.py`，可手动调用�?
- 检查今�?`docs/plans/YYYY-MM-DD-*.md` 是否存在
- 白名单路径（`docs/`、`AGENTS.md`、`Version.md`、`.githooks/` 等）永远放行
- 源代码目录（`zip_rar_tool/`、`tests/`）必须有对应计划文件
- 退出码�?=放行  1=警告  2=BLOCK

手动检查：`python .opencode/hooks/workflow_check.py`

### Tier 3: Git pre-commit hook（最终防线）
位于 `.githooks/pre-commit`，commit 时自动执行：
1. 调用 `workflow_check.py --commit` 验证计划文件
2. 验证 AGENTS.md 声明的文件结构完�?
3. 运行全部测试（pytest），失败则阻�?commit

启用方式（初始化 git 仓库后执行一次）�?
```bash
git config core.hooksPath .githooks
```

### 自定义命�?
- `/check` �?运行工作流合规检�?

## OpenSpec 工作�?
本项目使�?OpenSpec 驱动开发，步骤如下�?
1. `/opsx-propose <change-name>` �?创建变更提案（proposal + design + tasks�?
2. `/opsx-apply <change-name>` �?实施任务（逐任务完成）
3. `/opsx-archive <change-name>` �?归档已完成变�?

## 注意事项
- unrar.exe 可从 https://www.rarlab.com/rar_add.htm 获取
- py7zr 是纯 Python 实现，无需外部依赖
- rarfile 库需 unrar.exe �?PATH 或同目录

## 行为准则 & 调试方法�?

见外部文件（compaction 安全）：`.opencode/rules/behavior.md`

## 开发工作流

### 0. 加载上下�?�?`openspec/specs/`
- 每次任务开始前，先读取 `openspec/specs/` 获取项目背景
- spec 是需求的地基，不�?spec 不动�?

### 1. 需求澄�?�?`ahthropics-skill-brainstorming`
- 与用�?brainstorm 确认真实需求，理解约束和优先级
- 不假设需求，不默默决�?

### 2. 提出方案 �?`/opsx:propose`
- 运行 `/opsx:propose <feature-name>` 生成�?
  - `proposal.md`（需�?+ 方向�?
  - `design.md`（架�?+ 方案�?
  - `tasks.md`（任务分解）
- 只生成这三个文件，不多不�?

### 3. 人工审查
- 用户确认 proposal.md 的需求和方向
- **唯一的人工卡�?*：方向错了当场纠正，不返�?
- [ ] 检查点：用户已批准



> **WARNING: 即使 docs/plans/ 有计划文件，也不得跳�?Steps 2-3 (propose -> review)�?*
> 已有计划文件 != 可以跳步。每项变更必须重新走完整流程�?

### 4. 制定计划 �?`superpowers-skills-writing-plans` **[GATE �?HOOK ENFORCED]**
- 基于 design 拆解原子 TDD 任务
- 计划保存�?`docs/plans/YYYY-MM-DD-<feature>.md`
- 用户明确同意后方可执�?
- [ ] **检查点：计划文件已存在�?docs/plans/ �?此后才能写代�?*

### 5. 执行计划 �?`superpowers-skills-subagent-driven-development`
- 每个子代理执行前**必须读取 `openspec/specs/`** 获取上下�?
- 逐任务执行，每完成一�?task �?commit

### 6. 测试验证（两层）
- **TDD（`superpowers-skills-test-driven-development`�?*�?
  写新代码前先写测试，保证新功能正�?
- **全量回归（`pytest tests/`�?*�?
  所有改动完成后跑全部测试，保证旧功能没�?
- 有任何一�?FAIL �?修好再继续，不到下一�?

### 7. 归档记忆 �?`/opsx:archive`
- delta spec 合并�?`openspec/specs/`，知识库自更�?
- 下一�?AI 任务自动读取，不再遗�?

### 8. 版本锚点 �?git
- `git commit` + 更新 `Version.md`
- `git tag vX.Y.Z`：出问题可精确回退

### 9. 调试（按需�?�?`my-systematic-debugging` + `superpowers-skills-systematic-debugging`
- 遇到 bug 时，同时调用两个 skill 定位根因
- 先查根因，再�?②→�?修复流程

### QUICK COMPLIANCE CHECK

在写代码之前，自查以下清单（全部 YES 才能动手）：

- [ ] 我读�?`openspec/specs/` 吗？（Step 0�?
- [ ] 我和用户做了 brainstorm 吗？（Step 1�?
- [ ] 我运行了 `/opsx:propose` 吗？（Step 2�?
- [ ] 用户批准�?proposal 吗？（Step 3�?
- [ ] **`docs/plans/YYYY-MM-DD-<feature>.md` 存在吗？（Step 4）← HOOK 强制检�?*

**如果任何一个答案是 NO，不要写代码。按顺序走完前面的步骤�?*

### 其他规则

- 执行范围内：当前项目目录下的任何增删查改操作�?*直接执行，无需询问**
- 执行范围外：任何修改当前项目以外文件的操作，必须先询问用�?
- 涉及文件变更时新建版本，不覆盖原文件，更�?`Version.md`
- 每次修改完成后必须执行：`git commit` + 更新 `Version.md`
- `Version.md` 中每个版本号对应一�?`git tag`，版本与 commit 一一对应
- Version.md 顶部必须有 **版本映射表**，列出 Version / Tag / Commit / Date 的对应关系
- 每条版本条目必须标注 	ag: vX.Y.Z 和 commit: <hash> 引用
- 版本发布时执行：git tag vX.Y.Z，并在 Version.md 中更新映射表 + 标注 tag 引用
- 保留所有历史版本文件，不删除，便于回滚
- 提交修改到本地 git
- **每次执行任务完成后，必须在回复末尾告知用户当前版本号**
