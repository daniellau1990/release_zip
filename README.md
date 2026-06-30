# release_zip

ZIP / RAR / 7z 压缩解压工具，Python 3.10+，带 GUI 界面。

## 功能

- **解压** — 支持 ZIP、RAR、7z，可拖拽文件到窗口
- **压缩** — 支持 ZIP（内置）、7z（py7zr），可选密码保护
- **查看** — 列出压缩包内文件，含文件名、大小、压缩后大小
- **进度条** — 实时显示解压/压缩进度

## 技术栈

| 组件 | 技术 |
|------|------|
| CLI | [typer](https://github.com/fastapi/typer) |
| GUI | [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) + tkinterdnd2 |
| ZIP | `zipfile` (Python 标准库) |
| RAR 解压 | [rarfile](https://github.com/markokr/rarfile) + [unrar.exe](https://www.rarlab.com/) |
| 7z | [py7zr](https://github.com/miurahr/py7zr) |
| 打包 | [PyInstaller](https://pyinstaller.org/) |

## 安装

```bash
# 克隆仓库
git clone https://github.com/daniellau1990/release_zip.git
cd release_zip

# 创建虚拟环境并安装
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -e .
```

## 使用

### GUI

```bash
python -m gui
```

### CLI

```bash
# 解压
python -m zip_rar_tool extract archive.rar -o ./output

# 压缩
python -m zip_rar_tool compress ./folder -o output.zip

# 查看压缩包内容
python -m zip_rar_tool list archive.zip
```

## 平台支持

| 格式 | 解压 | 压缩 |
|------|------|------|
| ZIP | 全平台 | 全平台 |
| RAR | Windows (x64) | 需系统安装 WinRAR |
| 7z | 全平台 | 全平台 |

RAR 解压依赖 `bin/unrar.exe`（Windows x64），由 RARLabs 免费分发。其他平台用户需自行安装 `unrar` 命令行工具。

## 许可证

本项目代码使用 MIT License。`bin/unrar.exe` 版权归 Alexander Roshal (RARLabs) 所有，可自由分发，详见 [license.txt](license.txt)。
