## Context

排查发现 4 个 bug:
1. `Path(".zip").suffix` 返回空，因 pathlib 视点开头的文件无后缀
2. `echo %files%|` 管道中 `echo` 输出 GBK 编码，Python stdin 读 UTF-8，中文路径损坏
3. `set /p` 只读一行，多文件换行分隔时只取第一个
4. `.bat` 用 `cd /d "%~dp0"` 切换目录，输出在项目目录而非用户目录

## Goals / Non-Goals

**Goals:**
- 中文文件路径压缩成功
- 输入 `a` 自动输出 `a.zip`（无后缀时默认 `.zip`）
- 提示语标明支持的格式和示例
- 输出文件在用户当前目录
- 保留测试日志到 `docs/test-logs/`

**Non-Goals:**
- 不修改 extract/list 功能
- 不修改现有测试

## Decisions

- **改管道为临时文件**：`.bat` 把 `%files%` 写入临时文件（`%TEMP%\zip_rar_files_%RANDOM%.txt`），Python 从此文件读取。临时文件写入时用当前系统编码（`chcp`），但 Python 以 `utf-8` 解码读回。实际上更简单：.bat 创建临时文件并写入 `%files%`，Python 直接读文件内容按空格+换行分隔。
- **自动补后缀**：Python 检查 `out.suffix`，如果为空则在文件名后加 `.zip`。
- **提示修改**：`Output filename (supported: .zip, .7z, e.g. myarchive.zip):`
- **输出路径**：.bat 不再依赖 `cd /d "%~dp0"` 的副作用，Python 用显式路径。
- **写临时文件用 UTF-8**：用 `chcp 65001` 确保临时文件编码一致。

## Risks

- **[Low] 临时文件残留**：压缩完成后删除，异常时可能残留。
