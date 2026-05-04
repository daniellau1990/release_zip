# ZIP/RAR/7z 工具 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python library + CLI tool for compressing/extracting ZIP, RAR, and 7z archives

**Architecture:** Strategy pattern with one backend per format, unified by ArchiveHandler in core.py. CLI via typer, public API exposed via `__init__.py`.

**Tech Stack:** Python 3.10+, typer, zipfile (stdlib), rarfile, py7zr, pytest

---

### Task 1: Project scaffold & dependencies

**Files:**
- Create: `pyproject.toml`
- Create: `zip_rar_tool/__init__.py` (stub)
- Create: `zip_rar_tool/__main__.py` (stub)

**Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.backends._legacy:_Backend"

[project]
name = "zip-rar-tool"
version = "0.1.0"
description = "Extract and compress ZIP, RAR, 7z archives"
requires-python = ">=3.10"
dependencies = [
    "typer>=0.9",
    "rarfile>=4.2",
    "py7zr>=0.22",
]

[project.scripts]
zip-rar-tool = "zip_rar_tool.cli:app"

[tool.setuptools.packages.find]
include = ["zip_rar_tool*"]

[tool.setuptools.package-data]
"zip_rar_tool" = ["py.typed"]
```

**Step 2: Create __init__.py stub**

```python
VERSION = "0.1.0"
```

**Step 3: Create __main__.py stub**

```python
from .cli import app
app()
```

**Step 4: Create directory structure**

```
zip_rar_tool/
  __init__.py
  __main__.py
  cli.py          (stub)
  core.py         (stub)
  backends/
    __init__.py
    zip_backend.py
    rar_backend.py
    sevenz_backend.py
  utils.py
tests/
  __init__.py
bin/
  (empty - unrar.exe will be placed manually)
```

Run: `python -c "import zip_rar_tool; print('OK')"`
Expected: OK

**Step 5: Commit**

```bash
git add -A
git commit -m "chore: scaffold project structure"
```

---

### Task 2: Utils module

**Files:**
- Create: `zip_rar_tool/utils.py`

**Step 1: Write utils.py**

```python
from pathlib import Path


def safe_path(destination: Path, filename: str) -> Path:
    cleaned = Path(filename).name
    return destination / cleaned


def guess_format(path: str) -> str:
    ext = Path(path).suffix.lower()
    if ext == ".zip":
        return "zip"
    elif ext == ".rar":
        return "rar"
    elif ext == ".7z":
        return "7z"
    raise ValueError(f"Unsupported format: {ext}")
```

---

### Task 3: ZIP backend (extract + list + compress)

**Files:**
- Create: `zip_rar_tool/backends/zip_backend.py`
- Create: `tests/test_zip_backend.py`

**Step 1: Write the failing test**

```python
import pytest
from pathlib import Path
from zip_rar_tool.backends.zip_backend import ZipBackend


def test_zip_roundtrip(tmp_path):
    src = tmp_path / "src"
    src.mkdir()
    (src / "hello.txt").write_text("world", encoding="utf-8")
    archive = tmp_path / "test.zip"
    out = tmp_path / "out"

    ZipBackend.compress(src, archive)
    ZipBackend.extract(archive, out)

    assert (out / "hello.txt").read_text(encoding="utf-8") == "world"


def test_zip_list(tmp_path):
    archive = tmp_path / "test.zip"
    ZipBackend.compress(tmp_path, archive)
    files = ZipBackend.list_files(archive)
    assert isinstance(files, list)
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_zip_backend.py -v`
Expected: FAIL with ModuleNotFoundError or ImportError

**Step 3: Write minimal implementation**

```python
from pathlib import Path
import zipfile
from zip_rar_tool.utils import safe_path


class ZipBackend:
    @staticmethod
    def extract(archive_path: Path, output_dir: Path, password: str | None = None) -> None:
        with zipfile.ZipFile(archive_path, "r") as zf:
            if password:
                zf.setpassword(password.encode("utf-8"))
            zf.extractall(output_dir)

    @staticmethod
    def list_files(archive_path: Path) -> list[dict]:
        result = []
        with zipfile.ZipFile(archive_path, "r") as zf:
            for info in zf.infolist():
                result.append({
                    "filename": info.filename,
                    "size": info.file_size,
                    "compressed_size": info.compress_size,
                })
        return result

    @staticmethod
    def compress(source_dir: Path, output_path: Path, password: str | None = None) -> None:
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in source_dir.rglob("*"):
                if file_path.is_file():
                    arcname = str(file_path.relative_to(source_dir))
                    zf.write(file_path, arcname)
```

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_zip_backend.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add -A
git commit -m "feat: add zip backend"
```

---

### Task 4: RAR backend (extract + list)

**Files:**
- Create: `zip_rar_tool/backends/rar_backend.py`
- Create: `tests/test_rar_backend.py`

**Step 1: Write the failing test**

```python
def test_rar_extract(mock_rar_archive):
    ...
```

**Step 2: Write minimal implementation**

```python
from pathlib import Path
import rarfile


class RarBackend:
    @staticmethod
    def extract(archive_path: Path, output_dir: Path, password: str | None = None) -> None:
        with rarfile.RarFile(archive_path) as rf:
            if password:
                rf.setpassword(password)
            rf.extractall(output_dir)

    @staticmethod
    def list_files(archive_path: Path) -> list[dict]:
        result = []
        with rarfile.RarFile(archive_path) as rf:
            for info in rf.infolist():
                result.append({
                    "filename": info.filename,
                    "size": info.file_size,
                    "compressed_size": info.compress_size,
                })
        return result

    @staticmethod
    def compress(source_dir: Path, output_path: Path, password: str | None = None) -> None:
        raise NotImplementedError("RAR compression requires WinRAR to be installed")
```

**Step 3: Include winrar check for compress**

```python
def _check_winrar() -> str | None:
    import winreg
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WinRAR") as key:
            path = winreg.QueryValueEx(key, "exe32")[0]
            return path
    except (OSError, FileNotFoundError):
        return None
```

---

### Task 5: 7z backend (extract + list + compress)

**Files:**
- Create: `zip_rar_tool/backends/sevenz_backend.py`

```python
from pathlib import Path
import py7zr


class SevenzBackend:
    @staticmethod
    def extract(archive_path: Path, output_dir: Path, password: str | None = None) -> None:
        with py7zr.SevenZipFile(archive_path, mode="r", password=password) as sz:
            sz.extractall(output_dir)

    @staticmethod
    def list_files(archive_path: Path) -> list[dict]:
        result = []
        with py7zr.SevenZipFile(archive_path, mode="r") as sz:
            for info in sz.list():
                result.append({
                    "filename": info.filename,
                    "size": info.uncompressed,
                    "compressed_size": info.compressed,
                })
        return result

    @staticmethod
    def compress(source_dir: Path, output_path: Path, password: str | None = None) -> None:
        with py7zr.SevenZipFile(output_path, mode="w", password=password) as sz:
            sz.writeall(source_dir, arcname=source_dir.name)
```

---

### Task 6: Core module (ArchiveHandler)

**Files:**
- Create: `zip_rar_tool/core.py`

```python
from pathlib import Path
from zip_rar_tool.utils import guess_format
from zip_rar_tool.backends.zip_backend import ZipBackend
from zip_rar_tool.backends.rar_backend import RarBackend
from zip_rar_tool.backends.sevenz_backend import SevenzBackend

BACKENDS = {
    "zip": ZipBackend,
    "rar": RarBackend,
    "7z": SevenzBackend,
}


def extract(archive_path: str, output_dir: str, password: str | None = None) -> None:
    fmt = guess_format(archive_path)
    backend = BACKENDS[fmt]
    backend.extract(Path(archive_path), Path(output_dir), password)


def list_files(archive_path: str) -> list[dict]:
    fmt = guess_format(archive_path)
    backend = BACKENDS[fmt]
    return backend.list_files(Path(archive_path))


def compress(source_dir: str, output_path: str, password: str | None = None) -> None:
    fmt = guess_format(output_path)
    backend = BACKENDS[fmt]
    backend.compress(Path(source_dir), Path(output_path), password)
```

---

### Task 7: CLI module (typer)

**Files:**
- Create: `zip_rar_tool/cli.py`

```python
import typer
from zip_rar_tool import core

app = typer.Typer()


@app.command()
def extract(
    archive: str = typer.Argument(..., help="Path to archive file"),
    output: str = typer.Argument(".", help="Output directory"),
    password: str = typer.Option(None, "--password", "-p", help="Archive password"),
):
    core.extract(archive, output, password)
    typer.echo(f"Extracted to {output}")


@app.command()
def list(
    archive: str = typer.Argument(..., help="Path to archive file"),
):
    files = core.list_files(archive)
    for f in files:
        typer.echo(f"{f['filename']:50s} {f['size']:>10d}")


@app.command()
def compress(
    source: str = typer.Argument(..., help="Source directory"),
    output: str = typer.Argument(..., help="Output archive path"),
    password: str = typer.Option(None, "--password", "-p", help="Archive password"),
):
    core.compress(source, output, password)
    typer.echo(f"Created {output}")
```

---

### Task 8: Wire __init__.py public API

**Files:**
- Modify: `zip_rar_tool/__init__.py`

```python
from zip_rar_tool.core import extract, list_files, compress

VERSION = "0.1.0"

__all__ = ["extract", "list_files", "compress"]
```

---

### Task 9: Download unrar.exe

**Step 1:** Download unrar.exe from RARLAB and place in `bin/`

```bash
# Download from https://www.rarlab.com/rar_add.htm
# Place at bin/unrar.exe
```

---

### Task 10: Integration test

**Files:**
- Create: `tests/test_integration.py`

Test roundtrip: compress folder → zip/7z, list, extract, verify content.
