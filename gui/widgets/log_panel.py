import customtkinter as ctk


class LogPanel(ctk.CTkFrame):
    """底部可折叠日志面板"""

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._collapsed = True

        self._toggle_btn = ctk.CTkButton(
            self, text="+ 日志", width=60, command=self._toggle
        )
        self._toggle_btn.pack(side="left", padx=(0, 5))

        self._textbox = ctk.CTkTextbox(self, height=0)

    def log(self, message: str):
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
