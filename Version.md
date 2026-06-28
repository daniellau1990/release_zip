# Version History

## 版本映射

| Version | Git Tag | Commit | Time (UTC+8) |
|---------|:-------:|:------:|--------------|
| v0.2.4  | v0.2.4 | bb70498 | 2026-06-28 11:30:21 |
| v0.2.3  | v0.2.3 | f8c7b64 | 2026-05-06 19:16:21 |
| v0.2.2  | v0.2.2 | 30c4972 | 2026-05-06 18:43:33 | **STABLE** |
| v0.2.1  | v0.2.1 | 3d573a1 | 2026-05-06 18:26:39 |
| v0.2.0  | v0.2.0 | 055e579 | 2026-05-06 14:33:19 |
| v0.1.4  | v0.1.4 | ad9974e | 2026-05-06 00:38:51 |
| v0.1.3  | v0.1.3 | 6103e72 | 2026-05-05 20:01:47 |
| v0.1.2  | v0.1.2 | 952c58a | 2026-05-05 19:22:25 |
| v0.1.1  | v0.1.1 | 8dc2aad | 2026-05-05 12:22:57 |
| v0.1.0  | v0.1.0 | 6688038 | 2026-05-04 23:01:48 |

---

## v0.2.4 (2026-06-28 11:30:21) tag: v0.2.4

- CLAUDE.md 全面改造：迁移 replace_txt 项目的工作流和规则
  - Feature / Bug Fix 双轨开发工作流
  - 设计探针（Feature Step 2）—— 不熟悉 API 不带假设编码
  - 十问根因分析法 + Debug 后三步（lesson-learned + 规则自检）
  - 常见错误模式及预防（速度偏见 / "简单修复"幻觉 / 文字游戏 / 自欺式自检）
  - 硬规则（探针/诊断/功能测试不可跳过；widget/layout/thread/callback/event 零容忍）
  - Behavioral Guidelines（Think Before Coding / Simplicity First / Surgical Changes / Goal-Driven Execution）
  - 代码审查清单（6 项，每项附命令+输出证据）
  - 三层测试体系（单元 / 功能 / 用户场景）
  - "已完成" 证据标准（不可凭"代码看起来对"就宣布完成）
  - HOOK 保护（精简为 Version.md 检查，移除三层防御方案）
  - 日志规则增强（轮转、版本号标注）
- 移除：OpenCode 三层防御方案、OpenSpec 工作流、QUICK COMPLIANCE CHECK

---

## v0.2.3 (2026-05-06 19:16:21) tag: v0.2.3 commit: f8c7b64

- Fix: extract output relative path now resolves relative to archive's directory
- Root cause: `output=1` (relative) resolved against .bat CWD (project dir), not archive dir
- Same fix pattern as v0.1.4 batch_compress.py, now applied to core.extract
- 用户反馈: 已验证，解压输出正确到压缩包所在文件夹

---

## v0.2.2 (2026-05-06 18:43:33) tag: v0.2.2 commit: 30c4972 **[STABLE]**

- Fix: strip drag-drop `"` from archive/files after set /p
- Fix: use full %date% instead of truncated ~0,10 for LOGFILE filename
- Root cause: drag-drop quotes cause CMD double-quoting -> Typer arg count mismatch
- 用户反馈: 可以正常解压缩，提取成功。提取结果在 C:\Users\surface\Desktop\新建文件夹 (2)，确认 v0.2.2 解压功能正常工作
- 遗留问题: 当用户输入相对路径作为 output（如 `1`）时，文件解压到项目目录而非压缩包所在目录。此问题在 v0.2.3 修复

---

## v0.2.1 (2026-05-06 18:26:39) tag: v0.2.1 commit: 3d573a1

- Fix: Chinese locale %date% slash breaks LOGFILE path, prevents all commands from running
- Fix: add mkdir logs/runs/ defense before first log write
- Root cause: %date% = 2026/05/06, / interpreted as dir separator in CMD redirect

---

## v0.1.1 (2026-05-05 12:22:57) tag: v0.1.1 commit: 8dc2aad

- Fix: multi-file compress crash when dragging into .bat (stdin + shlex)
- Add: tests/test_batch_compress.py (5 test cases)
- Change: batch_compress.py reads from stdin instead of sys.argv

---

## v0.1.0 (2026-05-04 23:01:48) tag: v0.1.0 commit: 6688038

- Initial release: ZIP/RAR/7z extract, compress, list
- Interactive .bat menu with drag-drop support
- Multi-file compression (option B)
- Three-tier defense system (AGENTS.md hooks + plugin + pre-commit)
- CLI: extract/list/compress commands
## v0.1.2 (2026-05-05 19:22:25) tag: v0.1.2 commit: 952c58a

- Fix: Chinese path encoding (temp file instead of echo pipe)
- Fix: auto-append ".zip" when output has no suffix
- Fix: multi-file drag-drop via for loop in .bat
- Add: test_logs/ directory for test output retention
- Add: 5 batch_compress tests (single, multi, folder, auto-suffix, quoted)

## v0.1.3 (2026-05-05 20:01:47) tag: v0.1.3 commit: 6103e72

- Fix: output path now uses user's working directory (not project dir)
- Fix: drag-drop concatenated paths "quoted"adjacent parsed correctly
- Change: regex instead of shlex.split for Windows path parsing

## v0.1.4 (2026-05-06 00:38:51) tag: v0.1.4 commit: ad9974e

- Fix: output auto-saves to first input file's directory (even if .bat runs elsewhere)

## v0.2.0 (2026-05-06 14:33:19) tag: v0.2.0 commit: 055e579

- **BREAKING FIX**: if defined instead of quoted if (cmd crash from drag-drop quotes)
- Add: run_log.txt >> append mode (never overwrite old logs)
- Add: debugging 5-whys principle to AGENTS.md