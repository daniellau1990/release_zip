import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox

from zip_rar_tool import extract


class ExtractTab(ctk.CTkFrame):
    def __init__(self, parent, log_panel, **kwargs):
        super().__init__(parent, **kwargs)
        self.log = log_panel
        self._running = False

        self._archive_label = ctk.CTkLabel(self, text="未选择压缩包")
        self._archive_label.pack(pady=(20, 5))
        ctk.CTkButton(self, text="选择压缩包", command=self._choose_archive).pack()

        out_frame = ctk.CTkFrame(self)
        out_frame.pack(pady=10)
        ctk.CTkLabel(out_frame, text="解压到：").pack(side="left", padx=(0, 5))
        self._output_var = ctk.StringVar(value="")
        ctk.CTkEntry(out_frame, textvariable=self._output_var, width=300).pack(
            side="left", padx=(0, 5)
        )
        ctk.CTkButton(out_frame, text="浏览", width=60, command=self._choose_output).pack(
            side="left"
        )

        pwd_frame = ctk.CTkFrame(self)
        pwd_frame.pack(pady=5)
        ctk.CTkLabel(pwd_frame, text="密码（可选）：").pack(side="left", padx=(0, 5))
        self._password_var = ctk.StringVar(value="")
        ctk.CTkEntry(pwd_frame, textvariable=self._password_var, width=200, show="*").pack(
            side="left"
        )

        self._progress = ctk.CTkProgressBar(self, width=400)
        self._progress.set(0)
        self._progress.pack(pady=10)

        self._status_label = ctk.CTkLabel(self, text="")
        self._status_label.pack()

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
            base = os.path.splitext(os.path.basename(path))[0]
            self._output_var.set(os.path.join(os.path.dirname(path), base))

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
