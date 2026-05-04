# ZIP/RAR/7z 压缩解压工具 — 设计文档

## 目标
构建一个 Python 库 + CLI 工具，支持 ZIP/RAR/7z 三种格式的解压和查看，以及 ZIP/7z 的压缩（RAR 压缩条件性支持）。

## 技术选型
- **CLI 框架**：typer（基于类型注解，简洁现代）
- **ZIP**：zipfile（Python 标准库，零依赖）
- **RAR 解压**：rarfile + unrar.exe（免费分发）
- **7z**：py7zr（纯 Python，零外部依赖）
- **RAR 压缩**：检测系统 WinRAR（读注册表），条件性提供

## 架构设计

```
zip_rar_tool/
├── __init__.py          # 暴露 extract()、list_files()、compress()
├── __main__.py          # python -m zip_rar_tool 入口
├── cli.py               # typer CLI 定义
├── core.py              # ArchiveHandler 统一调度入口
├── backends/
│   ├── __init__.py      # 注册所有 backend
│   ├── zip_backend.py   # zipfile 封装
│   ├── rar_backend.py   # rarfile + unrar.exe 封装
│   └── sevenz_backend.py # py7zr 封装
└── utils.py             # 编码处理、路径工具
```

## 核心流程

### 解压流程
```
用户输入文件 → core.py 检测后缀
  ├── .zip  → zip_backend.extract()
  ├── .rar  → rar_backend.extract()
  └── .7z   → sevenz_backend.extract()
```

### 压缩流程
```
用户输入文件夹 → core.py 检测目标格式
  ├── .zip  → zip_backend.compress()
  ├── .7z   → sevenz_backend.compress()
  └── .rar  → rar_backend.compress()  ← 条件性，需检测 WinRAR
```

## Backend 接口约定

每个 backend 实现统一接口：

```python
class XxxBackend:
    @staticmethod
    def extract(archive_path: Path, output_dir: Path, password: str | None = None) -> None
    
    @staticmethod
    def list_files(archive_path: Path) -> list[FileInfo]
    
    @staticmethod
    def compress(source_dir: Path, output_path: Path, password: str | None = None) -> None
```

## RAR 压缩策略
1. 尝试读取注册表 `HKEY_LOCAL_MACHINE\SOFTWARE\WinRAR` → 获取安装路径
2. 找到 `rar.exe` 后调用系统 WinRAR 执行压缩
3. 未找到则抛出清晰提示，建议用户改用 zip/7z

## 中文编码处理
- **RAR**：使用 CP936（GBK）编码文件名
- **ZIP**：使用 UTF-8 编码
- **7z**：py7zr 自动处理 Unicode

## 依赖清单
```toml
[project]
dependencies = [
    "typer>=0.9",
    "rarfile>=4.2",
    "py7zr>=0.22",
]
```

## 未来扩展
- GUI 界面（CustomTkinter）
- 测试套件（pytest）
- 进度条显示
- 分卷压缩支持
