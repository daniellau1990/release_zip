# DEBUG.md — 提取失败 + 无运行日志

> 调查版本: v0.2.2
> 调查时间: 2026-05-06 18:30~18:45 UTC+8

---

## Observations

### 复现步骤

1. 运行 `zip-rar-tool.bat`
2. 选择 `1` (Extract)
3. 拖入 ZIP 文件: `"C:\Users\surface\Desktop\新建文件夹 (2)\pi-autoresearch-main.zip"`
4. 输入 output: `1`

### 实际结果（v0.2.0 首次测试）

```
Archive path (drag file here): "C:\Users\surface\Desktop\新建文件夹 (2)\pi-autoresearch-main.zip"
The system cannot find the path specified.
Output dir (Enter for default - archive name): 1
The system cannot find the path specified.
The system cannot find the path specified.
The system cannot find the path specified.
```

- **4 次** "The system cannot find the path specified."
- Python 提取命令从未执行
- `logs/runs/` 目录为空

### 环境

- OS: Windows 10 中文版 (10.0.19045)
- Locale: zh-CN
- `%date%` 格式: `2026/05/06 周三`（斜杠分隔，带中文星期）

---

## Root Cause #1: 中文日期斜杠 → LOGFILE 路径无效

### 问题链（五问五答）

| # | 为什么？ | 答案 |
|---|---------|------|
| Q1 | 为什么 Python 提取命令没执行？ | CMD 解析 `>> "%LOGFILE%"` 重定向时失败，整个命令被拦截 |
| Q2 | 为什么 LOGFILE 路径无效？ | `%date%` = `2026/05/06`，`/` 在 Windows 路径中是目录分隔符 |
| Q3 | 为什么 v0.1.1 没问题？ | v0.1.1 没有日志功能，无重定向，Python 直接执行 |
| Q4 | 为什么正好 4 次错误？ | .bat 中 4 处 `>> "%LOGFILE%"` 对应 4 次 CMD 重定向失败 |
| Q5 | `>>` 为什么不自动创建目录？ | CMD 的重定向不会 mkdir -p，目录不存在则失败 |

### 实验验证

```python
# Test A: / in filename
subprocess.run('echo test >> "logs/runs/run_log_2026/05/06.txt"', shell=True)
# → rc=1, stderr="系统找不到指定的路径。"

# Test B: - in filename
subprocess.run('echo test >> "logs/runs/run_log_2026-05-06.txt"', shell=True)
# → rc=0, 文件创建成功
```

### 修复 (v0.2.1)

- `%date:/=-%` 替换斜杠为横杠
- `%date: =_%` 替换空格为下划线（防止中文星期名中的空格）
- 防御性 `mkdir logs/runs/` 在首次写入前

---

## Root Cause #2: 拖放引号 → CMD 参数分裂 → Typer 报错

### 实际日志（v0.2.1 修复 LOGFILE 后）

```
[EXTRACT] archive="C:\Users\surface\Desktop\新建文件夹 (2)\pi-autoresearch-main.zip"
[EXTRACT] output=1
Usage: python -m zip_rar_tool extract [OPTIONS] ARCHIVE [OUTPUT]
Error: Got unexpected extra argument (1)
[EXTRACT] done rc=2
```

### 问题链

| # | 为什么？ | 答案 |
|---|---------|------|
| Q1 | 为什么 Typer 报 "unexpected extra argument (1)"？ | CMD 传了 3 个参数给 Typer，而非 2 个 |
| Q2 | 为什么会多一个参数？ | `%archive%` 含拖放引号 `"C:\..."`, `.bat` 再套 `"%archive%"` → `""C:\...""` |
| Q3 | CMD 如何解析 `""..."..."`？ | CMD 把 `""` 解析为转义引号 → 引号边界错位 → 路径被拆成多段 |
| Q4 | v0.1.1 同样有 `"%archive%"`, 为什么没报错？ | 用户可能手工输入路径（无引号），或没有空格路径不触发拖放加引号 |

### 实验验证

```python
# Simulate old .bat (no strip)
archive_raw = '"C:\Users\surface\Desktop\新建文件夹 (2)\test.zip"'  # drag-drop quotes
subprocess.run(['python', '-m', 'zip_rar_tool', 'extract', archive_raw, output])
# → rc=1, "ValueError: Unsupported format: .zip\""

# Simulate fixed .bat (strip quotes then re-quote)
archive_clean = archive_raw.replace('"', '')
subprocess.run(['python', '-m', 'zip_rar_tool', 'extract', archive_clean, output])
# → rc=0, "Extracted to ..."  ✅
```

### 修复 (v0.2.2)

- 所有 `set /p` 读取路径后立即 `set "var=%var:"=%"` 剥除拖放引号
- 涉及: EXTRACT (archive), LIST (archive), COMPRESS (files)

---

## 最终修复汇总

| 版本 | Bug | 修复 |
|------|-----|------|
| v0.2.1 | 中文 `%date%` 斜杠 → LOGFILE 路径无效 | `/` → `-`, 空格 → `_`, mkdir 防御 |
| v0.2.2 | 拖放引号 → CMD 参数分裂 → Typer 报错 | `set /p` 后 `set "v=%v:"=%"` 剥引号 |

### 经验教训

1. **日志本身也可能引入 bug** — v0.2.0 新增的 LOGFILE 重定向导致所有命令瘫痪
2. **locale 差异是关键** — 英文 Windows `%date%` 用 `-` 分隔，中文用 `/`，代码需要跨 locale 测试
3. **CMD 的引号解析极其脆弱** — `""..."..."` 不是嵌套引号，是参数分裂
4. **运行日志的价值** — v0.2.1 的 LOGFILE 修复让 v0.2.2 的诊断变得简单，直接看到 Typer 报错

---

## 相关版本

- v0.1.1 (2026-05-05 12:22:57) — 最后一次正常工作
- v0.2.0 (2026-05-06 14:33:19) — 引入日志功能，引入 Bug #1
- v0.2.1 (2026-05-06 18:26:39) — 修复 Bug #1，暴露 Bug #2
- v0.2.2 (2026-05-06 18:43:33) — 修复 Bug #2
