## Why

多文件压缩功能在交互式 .bat 中崩溃：拖入多个文件后按回车，cmd 窗口直接关闭。根因是 `%files%` 无引号导致 cmd 解析特殊字符时语法错误。同时，`batch_compress.py` 没有任何测试覆盖。

## What Changes

- `zip_rar_tool/batch_compress.py`：改从 `stdin` 读取输入路径，用 `shlex.split()` 解析，绕过 cmd 参数解析问题
- `zip-rar-tool.bat`：COMPRESS 段改管道传递输入
- `tests/test_batch_compress.py`：新增测试（单文件、多文件、混合文件+文件夹）

## Capabilities

### Modified Capabilities

- `interactive-cli`: 修改多文件压缩的输入方式

## Impact

- 仅改动 3 个文件，不改动现有 backend/core 逻辑
