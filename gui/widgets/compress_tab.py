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

        self._folder_label = ctk.CTkLabel(self, text="未选择源文件夹")
        self._folder_label.pack(pady=(20, 5))
        ctk.CTkButton(self, text="选择源文件夹", command=self._choose_folder).pack()

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
