import customtkinter as ctk
from tkinter import filedialog

from zip_rar_tool import list_files


class BrowseTab(ctk.CTkFrame):
    """查看压缩包内容——纯预览"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

        ctk.CTkButton(self, text="选择压缩包", command=self._choose).pack(pady=(20, 10))
        self._archive_label = ctk.CTkLabel(self, text="未选择文件")
        self._archive_label.pack()

        hdr = ctk.CTkFrame(self)
        hdr.pack(fill="x", padx=20, pady=(15, 0))
        ctk.CTkLabel(hdr, text="文件名", width=350, anchor="w").pack(side="left")
        ctk.CTkLabel(hdr, text="大小", width=100, anchor="e").pack(side="right")

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

    def _format_size(self, size: int) -> str:
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"
