# GUI 界面实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 为 zip_rar_tool 添加 CustomTkinter 桌面 GUI，顶部三 Tab（解压/压缩/查看），真实进度条，pyinstaller 打包单文件 .exe。

**Architecture:** Core 层与 GUI 层完全解耦。Core 新增 `progress_callback` 可选参数，三个 backend 从 `extractall()` 改为逐文件操作以支持进度回调。GUI 层薄调用 core API，操作放在后台线程防止阻塞 UI。

**Tech Stack:** Python 3.10+, CustomTkinter, threading, pyinstaller

**Grilling Decisions:** 15 项（见 grilling session），`CONTEXT.md`（领域术语），`docs/adr/0001-gui-customtkinter.md`（框架选型）

---

### Task 1: 安装 CustomTkinter + 设计探针

**Files:**
- Modify: `setup.py` 或 `pyproject.toml`（添加依赖）

**Step 1: 安装**

```bash
.venv\Scripts\python.exe -m pip install customtkinter
```

**Step 2: 设计探针 — 验证关键 API 存在**

```python
# probe_ctk.py — 验证后删除
import customtkinter as ctk

# 1. 窗口和主题
app = ctk.CTk()
ctk.set_appearance_mode("system")
ctk.set_default_color_theme("blue")
assert hasattr(app, 'title'), "CTk.title missing"

# 2. Tabview（核心组件）
tv = ctk.CTkTabview(app)
tv.add("test")
assert hasattr(tv, 'tab'), "CTkTabview.tab missing"
assert callable(tv.tab), "CTkTabview.tab not callable"

# 3. ProgressBar
bar = ctk.CTkProgressBar(app)
bar.set(0.5)
assert bar.get() == 0.5, "CTkProgressBar.set/get mismatch"

# 4. Textbox（日志面板）
tb = ctk.CTkTextbox(app)
tb.insert("end", "log\n")
assert tb.get("1.0", "end-1c") == "log", "CTkTextbox readback failed"

# 5. after() method for thread-safe UI updates
assert hasattr(app, 'after'), "CTk.after missing (required for thread safety)"

print("ALL PROBES PASSED")
```

**Step 3: 运行探针**

```bash
.venv\Scripts\python.exe probe_ctk.py
```
Expected: `ALL PROBES PASSED`

**Step 4: 验证现有测试不受影响**

```bash
pytest tests/ -v
```
Expected: 16 passed

**Step 5: Commit**

```bash
git add -A
git commit -m "chore: add customtkinter dependency, API probes passed"
```

---

### Task 2: Core API — 添加 progress_callback 参数

**Files:**
- Modify: `zip_rar_tool/core.py:15-35`
- Create: `tests/test_progress_callback.py`

**Step 1: 写失败测试**

```python
# tests/test_progress_callback.py
from pathlib import Path
from zip_rar_tool import extract, compress

def test_extract_progress_callback(tmp_path):
    """progress_callback is called with (current, total) for each file."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("a")
    (src / "b.txt").write_text("b")
    archive = tmp_path / "test.zip"

    compress(str(src), str(archive))

    calls = []
    def cb(current, total):
        calls.append((current, total))

    out = tmp_path / "out"
    extract(str(archive), str(out), progress_callback=cb)

    assert len(calls) == 2, f"expected 2 calls, got {len(calls)}"
    assert calls[0] == (1, 2)
    assert calls[1] == (2, 2)


def test_extract_without_callback_still_works(tmp_path):
    """Backward compat: extract without progress_callback must not break."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "x.txt").write_text("hello")
    archive = tmp_path / "test.zip"

    compress(str(src), str(archive))

    out = tmp_path / "out"
    extract(str(archive), str(out))  # no callback

    assert (out / "x.txt").read_text() == "hello"


def test_compress_progress_callback(tmp_path):
    """Compress also supports progress_callback."""
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_text("a")
    (src / "b.txt").write_text("b")

    calls = []
    def cb(current, total):
        calls.append((current, total))

    archive = tmp_path / "test.zip"
    compress(str(src), str(archive), progress_callback=cb)

    assert len(calls) == 2
```

**Step 2: 运行测试确认失败**

```bash
pytest tests/test_progress_callback.py -v
```
Expected: FAIL（`compress() got an unexpected keyword argument 'progress_callback'`）

**Step 3: 修改 core.py**

```python
# zip_rar_tool/core.py
from pathlib import Path
from typing import Optional, Callable

from zip_rar_tool.utils import guess_format
from zip_rar_tool.backends.zip_backend import ZipBackend
from zip_rar_tool.backends.rar_backend import RarBackend
from zip_rar_tool.backends.sevenz_backend import SevenzBackend

BACKENDS = {
    "zip": ZipBackend,
    "rar": RarBackend,
    "7z": SevenzBackend,
}


def extract(
    archive_path: str,
    output_dir: str,
    password: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> str:
    out = Path(output_dir)
    if not out.is_absolute():
        archive_parent = Path(archive_path).parent
        out = archive_parent / out
    fmt = guess_format(archive_path)
    backend = BACKENDS[fmt]
    backend.extract(Path(archive_path), out, password, progress_callback=progress_callback)
    return str(out)


def list_files(archive_path: str) -> list:
    fmt = guess_format(archive_path)
    backend = BACKENDS[fmt]
    return backend.list_files(Path(archive_path))


def compress(
    source_dir: str,
    output_path: str,
    password: Optional[str] = None,
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> None:
    fmt = guess_format(output_path)
    backend = BACKENDS[fmt]
    backend.compress(Path(source_dir), Path(output_path), password, progress_callback=progress_callback)
```

**Step 4: 提交**

```bash
git add zip_rar_tool/core.py tests/test_progress_callback.py
git commit -m "feat: add progress_callback parameter to extract() and compress()"
```

---

### Task 3: ZIP Backend — 逐文件操作支持进度回调

**Files:**
- Modify: `zip_rar_tool/backends/zip_backend.py`

**当前状态**：`extract()` 用 `zf.extractall()`，`compress()` 已经在逐文件循环但无回调。

**Step 1: 改写 zip_backend.py**

```python
from pathlib import Path
import zipfile
from typing import Optional, List, Dict, Callable


class ZipBackend:
    @staticmethod
    def extract(
        archive_path: Path,
        output_dir: Path,
        password: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> None:
        with zipfile.ZipFile(archive_path, "r") as zf:
            if password:
                zf.setpassword(password.encode("utf-8"))
            members = zf.infolist()
            total = len(members)
            for i, member in enumerate(members, 1):
                zf.extract(member, output_dir)
                if progress_callback:
                    progress_callback(i, total)

    @staticmethod
    def list_files(archive_path: Path) -> List[Dict]:
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
    def compress(
        source_dir: Path,
        output_path: Path,
        password: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> None:
        file_paths = [p for p in source_dir.rglob("*") if p.is_file()]
        total = len(file_paths)
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for i, file_path in enumerate(file_paths, 1):
                arcname = str(file_path.relative_to(source_dir))
                zf.write(file_path, arcname)
                if progress_callback:
                    progress_callback(i, total)
```

**Step 2: 运行测试**

```bash
pytest tests/test_zip_backend.py tests/test_progress_callback.py -v
```
Expected: 4 passed

**Step 3: 提交**

```bash
git add zip_rar_tool/backends/zip_backend.py
git commit -m "feat: zip backend per-file operations with progress callback"
```

---

### Task 4: RAR Backend — 逐文件解压支持进度回调

**Files:**
- Modify: `zip_rar_tool/backends/rar_backend.py`

**Step 1: 改写 rar_backend.py 的 extract 方法**

```python
from pathlib import Path
from typing import Optional, List, Dict, Callable
import rarfile

_script_dir = Path(__file__).resolve().parent
_bin_dir = _script_dir.parents[1] / "bin"
_unrar_exe = str(_bin_dir / "unrar.exe")
if Path(_unrar_exe).exists():
    rarfile.UNRAR_TOOL = _unrar_exe


class RarBackend:
    @staticmethod
    def extract(
        archive_path: Path,
        output_dir: Path,
        password: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> None:
        with rarfile.RarFile(archive_path) as rf:
            if password:
                rf.setpassword(password)
            members = rf.infolist()
            total = len(members)
            for i, member in enumerate(members, 1):
                rf.extract(member, output_dir)
                if progress_callback:
                    progress_callback(i, total)

    @staticmethod
    def list_files(archive_path: Path) -> List[Dict]:
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
    def compress(source_dir: Path, output_path: Path, password: Optional[str] = None,
                 progress_callback: Optional[Callable[[int, int], None]] = None) -> None:
        raise NotImplementedError("RAR compression requires WinRAR to be installed")
```

**Step 2: 运行 RAR 测试**

```bash
pytest tests/test_rar_backend.py tests/test_progress_callback.py -v
```
Expected: RAR 相关通过（注意 test_progress_callback.py 只测 ZIP，RAR 测试用 fixtures）

**Step 3: 提交**

```bash
git add zip_rar_tool/backends/rar_backend.py
git commit -m "feat: rar backend per-file extract with progress callback"
```

---

### Task 5: 7z Backend — 逐文件操作支持进度回调

**Files:**
- Modify: `zip_rar_tool/backends/sevenz_backend.py`

**Step 1: 改写 sevenz_backend.py**

```python
from pathlib import Path
from typing import Optional, List, Dict, Callable
import py7zr


class SevenzBackend:
    @staticmethod
    def extract(
        archive_path: Path,
        output_dir: Path,
        password: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> None:
        with py7zr.SevenZipFile(archive_path, mode="r", password=password) as sz:
            members = sz.list()
            total = len(members)
            for i, member in enumerate(members, 1):
                sz.extract(output_dir, targets=[member.filename])
                if progress_callback:
                    progress_callback(i, total)

    @staticmethod
    def list_files(archive_path: Path) -> List[Dict]:
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
    def compress(
        source_dir: Path,
        output_path: Path,
        password: Optional[str] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> None:
        file_paths = [p for p in source_dir.rglob("*") if p.is_file()]
        total = len(file_paths)
        with py7zr.SevenZipFile(output_path, mode="w", password=password) as sz:
            for i, file_path in enumerate(file_paths, 1):
                sz.write(file_path, str(file_path.relative_to(source_dir)))
                if progress_callback:
                    progress_callback(i, total)
```

**Step 2: 运行 7z 测试**

```bash
pytest tests/test_sevenz_backend.py -v
```
Expected: 2 passed

**Step 3: 运行全部测试**

```bash
pytest tests/ -v
```
Expected: 18 passed（16 existing + 2 new progress_callback tests）

**Step 4: 提交**

```bash
git add zip_rar_tool/backends/sevenz_backend.py
git commit -m "feat: 7z backend per-file operations with progress callback"
```

---

### Task 6: GUI 主窗口骨架 + 日志面板

**Files:**
- Create: `gui/__init__.py`
- Create: `gui/app.py`
- Create: `gui/widgets/__init__.py`
- Create: `gui/widgets/log_panel.py`

**Step 1: gui/__init__.py**

```python
from gui.app import main
```

**Step 2: gui/widgets/__init__.py**

```python
# empty
```

**Step 3: gui/widgets/log_panel.py**

```python
import customtkinter as ctk


class LogPanel(ctk.CTkFrame):
    """底部可折叠日志面板"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._collapsed = True

        self._toggle_btn = ctk.CTkButton(
            self, text="+ 日志", width=80, command=self._toggle
        )
        self._toggle_btn.pack(side="left", padx=(0, 5))

        self._textbox = ctk.CTkTextbox(self, height=0)
        # 不 pack，默认隐藏

    def log(self, message: str):
        """追加一行日志"""
        self._textbox.insert("end", message + "\n")
        self._textbox.see("end")

    def error(self, message: str):
        self.log(f"[错误] {message}")
        if self._collapsed:
            self._toggle()

    def _toggle(self):
        self._collapsed = not self._collapsed
        if self._collapsed:
            self._textbox.pack_forget()
            self._toggle_btn.configure(text="+ 日志")
        else:
            self._textbox.configure(height=60)
            self._textbox.pack(fill="x", expand=False)
            self._toggle_btn.configure(text="- 日志")
```

**Step 4: gui/app.py**

```python
import sys
import customtkinter as ctk

from gui.widgets.log_panel import LogPanel


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("压缩解压工具")
        self.geometry("600x480")
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        # 顶部 Tab
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        self.tabview.add("解压")
        self.tabview.add("压缩")
        self.tabview.add("查看")

        # 占位标签（后续 Task 替换为实际 Widget）
        ctk.CTkLabel(self.tabview.tab("解压"), text="解压 Tab（实现中）").pack(pady=40)
        ctk.CTkLabel(self.tabview.tab("压缩"), text="压缩 Tab（实现中）").pack(pady=40)
        ctk.CTkLabel(self.tabview.tab("查看"), text="查看 Tab（实现中）").pack(pady=40)

        # 底部日志面板
        self.log_panel = LogPanel(self)
        self.log_panel.pack(fill="x", padx=10, pady=10)


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
```

**Step 5: 手工验证窗口**

```bash
.venv\Scripts\python.exe -m gui
```
Expected: 窗口弹出，显示三个 Tab 和日志面板按钮。关闭窗口正常退出。

**Step 6: 提交**

```bash
git add gui/
git commit -m "feat: GUI scaffold with tabs and log panel"
```

---

### Task 7: 解压 Tab Widget

**Files:**
- Create: `gui/widgets/extract_tab.py`
- Modify: `gui/app.py`（替换占位标签）

**Step 1: gui/widgets/extract_tab.py**

```python
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

from zip_rar_tool import extract


class ExtractTab(ctk.CTkFrame):
    def __init__(self, parent, log_panel, **kwargs):
        super().__init__(parent, **kwargs)
        self.log = log_panel
        self._running = False

        # 第1行：选择压缩包
        self._archive_label = ctk.CTkLabel(self, text="未选择压缩包")
        self._archive_label.pack(pady=(20, 5))
        ctk.CTkButton(self, text="选择压缩包", command=self._choose_archive).pack()

        # 第2行：输出目录
        self._output_var = ctk.StringVar(value="")
        out_frame = ctk.CTkFrame(self)
        out_frame.pack(pady=10)
        ctk.CTkLabel(out_frame, text="解压到：").pack(side="left", padx=(0, 5))
        ctk.CTkEntry(out_frame, textvariable=self._output_var, width=300).pack(
            side="left", padx=(0, 5)
        )
        ctk.CTkButton(out_frame, text="浏览", width=60, command=self._choose_output).pack(
            side="left"
        )

        # 第3行：密码
        pwd_frame = ctk.CTkFrame(self)
        pwd_frame.pack(pady=5)
        ctk.CTkLabel(pwd_frame, text="密码（可选）：").pack(side="left", padx=(0, 5))
        self._password_var = ctk.StringVar(value="")
        ctk.CTkEntry(pwd_frame, textvariable=self._password_var, width=200, show="*").pack(
            side="left"
        )

        # 第4行：进度条
        self._progress = ctk.CTkProgressBar(self, width=400)
        self._progress.set(0)
        self._progress.pack(pady=10)

        self._status_label = ctk.CTkLabel(self, text="")
        self._status_label.pack()

        # 第5行：解压按钮
        self._extract_btn = ctk.CTkButton(
            self, text="解压", width=120, command=self._on_extract
        )
        self._extract_btn.pack(pady=15)

        self._archive_path = None

    def _choose_archive(self):
        path = filedialog.askopenfilename(
            title="选择压缩包",
            filetypes=[
                ("所有支持的格式", "*.zip;*.rar;*.7z"),
                ("ZIP 文件", "*.zip"),
                ("RAR 文件", "*.rar"),
                ("7z 文件", "*.7z"),
            ],
        )
        if path:
            self._archive_path = path
            self._archive_label.configure(text=path)
            # 默认输出到同目录
            import os
            base = os.path.splitext(os.path.basename(path))[0]
            default_out = os.path.join(os.path.dirname(path), base)
            self._output_var.set(default_out)

    def _choose_output(self):
        path = filedialog.askdirectory(title="选择解压目标目录")
        if path:
            self._output_var.set(path)

    def _on_extract(self):
        if self._running:
            return
        if not self._archive_path:
            messagebox.showwarning("提示", "请先选择压缩包")
            return
        output = self._output_var.get().strip()
        if not output:
            messagebox.showwarning("提示", "请指定解压目标目录")
            return

        password = self._password_var.get().strip() or None

        self._running = True
        self._extract_btn.configure(state="disabled")
        self._progress.set(0)
        self._status_label.configure(text="准备中...")
        self.log.log(f"开始解压: {self._archive_path}")

        def run():
            try:
                extract(
                    self._archive_path,
                    output,
                    password=password,
                    progress_callback=self._on_progress,
                )
                self.after(0, self._on_done)
            except Exception as e:
                self.after(0, lambda: self._on_error(str(e)))

        threading.Thread(target=run, daemon=True).start()

    def _on_progress(self, current, total):
        self.after(0, lambda: self._update_progress(current, total))

    def _update_progress(self, current, total):
        self._progress.set(current / total)
        self._status_label.configure(text=f"正在解压 {current}/{total}...")

    def _on_done(self):
        self._running = False
        self._extract_btn.configure(state="normal")
        self._progress.set(1)
        self._status_label.configure(text="解压完成")
        self.log.log("解压完成")
        messagebox.showinfo("完成", "解压成功")

    def _on_error(self, msg):
        self._running = False
        self._extract_btn.configure(state="normal")
        self._status_label.configure(text="解压失败")
        self.log.error(msg)
        messagebox.showerror("解压失败", msg)
```

**Step 2: 更新 gui/app.py — 替换解压占位标签**

将 app.py 中：
```python
ctk.CTkLabel(self.tabview.tab("解压"), text="解压 Tab（实现中）").pack(pady=40)
```
替换为：
```python
from gui.widgets.extract_tab import ExtractTab
self.extract_tab = ExtractTab(self.tabview.tab("解压"), self.log_panel)
self.extract_tab.pack(fill="both", expand=True)
```

**Step 3: 提交**

```bash
git add gui/
git commit -m "feat: extract tab with file chooser, progress bar, threading"
```

---

### Task 8: 压缩 Tab Widget

**Files:**
- Create: `gui/widgets/compress_tab.py`
- Modify: `gui/app.py`（替换压缩占位标签）

**Step 1: gui/widgets/compress_tab.py**

```python
import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

from zip_rar_tool import compress


class CompressTab(ctk.CTkFrame):
    def __init__(self, parent, log_panel, **kwargs):
        super().__init__(parent, **kwargs)
        self.log = log_panel
        self._running = False

        # 第1行：选择文件夹
        self._folder_label = ctk.CTkLabel(self, text="未选择源文件夹")
        self._folder_label.pack(pady=(20, 5))
        ctk.CTkButton(self, text="选择源文件夹", command=self._choose_folder).pack()

        # 第2行：压缩格式 + 输出
        fmt_frame = ctk.CTkFrame(self)
        fmt_frame.pack(pady=10)
        ctk.CTkLabel(fmt_frame, text="格式：").pack(side="left", padx=(0, 5))
        self._format_var = ctk.StringVar(value="zip")
        self._format_menu = ctk.CTkOptionMenu(
            fmt_frame,
            values=["zip", "7z"],
            variable=self._format_var,
            command=self._on_format_changed,
        )
        self._format_menu.pack(side="left", padx=(0, 10))

        self._output_var = ctk.StringVar(value="")
        ctk.CTkEntry(fmt_frame, textvariable=self._output_var, width=250).pack(
            side="left", padx=(0, 5)
        )
        ctk.CTkButton(fmt_frame, text="浏览", width=60, command=self._choose_output).pack(
            side="left"
        )

        # 第3行：密码
        pwd_frame = ctk.CTkFrame(self)
        pwd_frame.pack(pady=5)
        ctk.CTkLabel(pwd_frame, text="密码（可选）：").pack(side="left", padx=(0, 5))
        self._password_var = ctk.StringVar(value="")
        ctk.CTkEntry(pwd_frame, textvariable=self._password_var, width=200, show="*").pack(
            side="left"
        )

        # 第4行：进度条
        self._progress = ctk.CTkProgressBar(self, width=400)
        self._progress.set(0)
        self._progress.pack(pady=10)

        self._status_label = ctk.CTkLabel(self, text="")
        self._status_label.pack()

        # 第5行：压缩按钮
        self._compress_btn = ctk.CTkButton(
            self, text="压缩", width=120, command=self._on_compress
        )
        self._compress_btn.pack(pady=15)

        self._folder_path = None

    def _on_format_changed(self, fmt):
        if self._folder_path:
            self._update_output_path()

    def _choose_folder(self):
        path = filedialog.askdirectory(title="选择要压缩的文件夹")
        if path:
            self._folder_path = path
            self._folder_label.configure(text=path)
            self._update_output_path()

    def _update_output_path(self):
        fmt = self._format_var.get()
        base = os.path.basename(self._folder_path)
        parent = os.path.dirname(self._folder_path)
        self._output_var.set(os.path.join(parent, f"{base}.{fmt}"))

    def _choose_output(self):
        fmt = self._format_var.get()
        path = filedialog.asksaveasfilename(
            title="保存压缩包",
            defaultextension=f".{fmt}",
            filetypes=[(f"{fmt.upper()} 文件", f"*.{fmt}")],
        )
        if path:
            self._output_var.set(path)

    def _on_compress(self):
        if self._running:
            return
        if not self._folder_path:
            messagebox.showwarning("提示", "请先选择源文件夹")
            return
        output = self._output_var.get().strip()
        if not output:
            messagebox.showwarning("提示", "请指定输出路径")
            return

        password = self._password_var.get().strip() or None

        self._running = True
        self._compress_btn.configure(state="disabled")
        self._progress.set(0)
        self._status_label.configure(text="准备中...")
        self.log.log(f"开始压缩: {self._folder_path} -> {output}")

        def run():
            try:
                compress(
                    self._folder_path,
                    output,
                    password=password,
                    progress_callback=self._on_progress,
                )
                self.after(0, self._on_done)
            except Exception as e:
                self.after(0, lambda: self._on_error(str(e)))

        threading.Thread(target=run, daemon=True).start()

    def _on_progress(self, current, total):
        self.after(0, lambda: self._update_progress(current, total))

    def _update_progress(self, current, total):
        self._progress.set(current / total)
        self._status_label.configure(text=f"正在压缩 {current}/{total}...")

    def _on_done(self):
        self._running = False
        self._compress_btn.configure(state="normal")
        self._progress.set(1)
        self._status_label.configure(text="压缩完成")
        self.log.log("压缩完成")
        messagebox.showinfo("完成", "压缩成功")

    def _on_error(self, msg):
        self._running = False
        self._compress_btn.configure(state="normal")
        self._status_label.configure(text="压缩失败")
        self.log.error(msg)
        messagebox.showerror("压缩失败", msg)
```

**Step 2: 更新 gui/app.py — 替换压缩占位标签**

```python
from gui.widgets.compress_tab import CompressTab
self.compress_tab = CompressTab(self.tabview.tab("压缩"), self.log_panel)
self.compress_tab.pack(fill="both", expand=True)
```

**Step 3: 提交**

```bash
git add gui/
git commit -m "feat: compress tab with format chooser, progress bar, threading"
```

---

### Task 9: 查看 Tab Widget

**Files:**
- Create: `gui/widgets/browse_tab.py`
- Modify: `gui/app.py`（替换查看占位标签）

**Step 1: gui/widgets/browse_tab.py**

```python
import customtkinter as ctk
from tkinter import filedialog

from zip_rar_tool import list_files


class BrowseTab(ctk.CTkFrame):
    """查看压缩包内容——纯预览，不可选择性解压"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        ctk.CTkButton(self, text="选择压缩包", command=self._choose).pack(pady=(20, 10))

        self._archive_label = ctk.CTkLabel(self, text="未选择文件")
        self._archive_label.pack()

        # 表头
        hdr = ctk.CTkFrame(self)
        hdr.pack(fill="x", padx=20, pady=(15, 0))
        ctk.CTkLabel(hdr, text="文件名", width=350, anchor="w").pack(side="left")
        ctk.CTkLabel(hdr, text="大小", width=100, anchor="e").pack(side="right")

        # 滚动列表
        self._list_frame = ctk.CTkScrollableFrame(self, height=250)
        self._list_frame.pack(fill="both", expand=True, padx=20, pady=5)

    def _choose(self):
        path = filedialog.askopenfilename(
            title="选择压缩包",
            filetypes=[
                ("所有支持的格式", "*.zip;*.rar;*.7z"),
                ("ZIP 文件", "*.zip"),
                ("RAR 文件", "*.rar"),
                ("7z 文件", "*.7z"),
            ],
        )
        if path:
            self._archive_label.configure(text=path)
            self._load(path)

    def _clear_list(self):
        for w in self._list_frame.winfo_children():
            w.destroy()

    def _format_size(self, size: int) -> str:
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"

    def _load(self, path: str):
        self._clear_list()
        try:
            files = list_files(path)
        except Exception as e:
            row = ctk.CTkFrame(self._list_frame)
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=f"读取失败: {e}", text_color="red").pack()
            return

        for f in files:
            row = ctk.CTkFrame(self._list_frame)
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(row, text=f["filename"], width=350, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=self._format_size(f["size"]), width=100, anchor="e").pack(
                side="right"
            )
```

**Step 2: 更新 gui/app.py — 替换查看占位标签**

```python
from gui.widgets.browse_tab import BrowseTab
self.browse_tab = BrowseTab(self.tabview.tab("查看"))
self.browse_tab.pack(fill="both", expand=True)
```

**Step 3: 提交**

```bash
git add gui/
git commit -m "feat: browse tab with scrollable file list"
```

---

### Task 10: 功能测试 + GUI 入口

**Files:**
- Modify: `zip_rar_tool/__init__.py`（更新 VERSION）
- Create: `gui/__main__.py`

**Step 1: gui/__main__.py**

```python
from gui.app import main

main()
```

**Step 2: 更新版本号**

`zip_rar_tool/__init__.py` 中 `VERSION = "0.3.0"`

**Step 3: 功能测试**

手工验证 GUI 应用：

```bash
.venv\Scripts\python.exe -m gui
```

操作清单：
- [ ] 窗口标题显示"压缩解压工具"
- [ ] 三个 Tab 可切换
- [ ] 解压 Tab：选压缩包 → 自动填输出目录 → 点解压 → 进度条跑 → 完成弹窗
- [ ] 压缩 Tab：选文件夹 → 自动填输出路径 → 选格式 → 点压缩 → 进度条跑 → 完成弹窗
- [ ] 查看 Tab：选压缩包 → 文件列表正确显示
- [ ] 密码：有密码的 ZIP/7z 可正常解压
- [ ] 错误：选损坏文件 → 弹窗报错 + 日志面板有详情
- [ ] 日志面板：点"+ 日志"展开 / "- 日志"折叠
- [ ] 主题跟随系统

**Step 4: 回归测试**

```bash
pytest tests/ -v
```
Expected: 18 passed

**Step 5: 提交**

```bash
git add gui/ zip_rar_tool/__init__.py
git commit -m "feat: GUI entry point, v0.3.0"
```

---

### Task 11: PyInstaller 打包

**Files:**
- Create: `build.spec` 或只用命令行

**Step 1: 安装 pyinstaller**

```bash
.venv\Scripts\python.exe -m pip install pyinstaller
```

**Step 2: 打包命令**

```bash
.venv\Scripts\pyinstaller.exe --onefile --windowed \
  --name "压缩解压工具" \
  --add-data "bin/unrar.exe;bin" \
  gui/__main__.py
```

**Step 3: 验证生成的 .exe**

```bash
dist\压缩解压工具.exe
```
Expected: GUI 正常启动，解压/压缩/查看功能正常

**Step 4: 提交**

```bash
git add -A
git commit -m "build: pyinstaller onefile packaging"
```

---

## Verification

所有任务完成后，完整验证：

```bash
# 1. 回归测试
pytest tests/ -v
# Expected: 18 passed

# 2. 启动 GUI
.venv\Scripts\python.exe -m gui
# Expected: 窗口显示，三 Tab 正常

# 3. 打包验证
.venv\Scripts\pyinstaller.exe --onefile --windowed --name "压缩解压工具" --add-data "bin/unrar.exe;bin" gui/__main__.py
# Expected: dist/压缩解压工具.exe 可独立运行
```
