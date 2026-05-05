## Why

多文件压缩功能存在 4 个 bug：`.zip` 后缀不识别、中文路径编码损坏导致 cmd 崩溃、`set /p` 只读第一行、输出路径在项目目录而非用户目录。

同时增加用户体验改进：输入 `a` 自动补 `.zip` 后缀、提示语标明支持的格式和示例。

## What Changes

- `.bat` COMPRESS 段：弃用 `echo %files%|` 管道，改为写临时 UTF-8 文件传递路径
- `batch_compress.py`：输入无后缀时默认补 `.zip`；从临时文件读路径（UTF-8 安全）
- 提示语改为 `Output filename (supported: .zip, .7z, e.g. myarchive.zip):`
- 输出路径位于用户当前目录（而非项目目录）
- 文档：创建 `docs/test-logs/` 目录规范

## Capabilities

### Modified Capabilities

- `interactive-cli`: 修复中文路径编码 + 输出路径定位 + 自动补后缀

## Impact

- 仅改动 zip-rar-tool.bat 和 batch_compress.py，不涉及 core/backend
