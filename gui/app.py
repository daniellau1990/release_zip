import customtkinter as ctk

from gui.widgets.log_panel import LogPanel
from gui.widgets.extract_tab import ExtractTab
from gui.widgets.compress_tab import CompressTab
from gui.widgets.browse_tab import BrowseTab


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("压缩解压工具")
        self.geometry("600x480")
        ctk.set_appearance_mode("system")
        ctk.set_default_color_theme("blue")

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=(10, 0))

        self.tabview.add("解压")
        self.tabview.add("压缩")
        self.tabview.add("查看")

        self.log_panel = LogPanel(self)
        self.log_panel.pack(fill="x", padx=10, pady=10)

        self.extract_tab = ExtractTab(self.tabview.tab("解压"), self.log_panel)
        self.extract_tab.pack(fill="both", expand=True)

        self.compress_tab = CompressTab(self.tabview.tab("压缩"), self.log_panel)
        self.compress_tab.pack(fill="both", expand=True)

        self.browse_tab = BrowseTab(self.tabview.tab("查看"))
        self.browse_tab.pack(fill="both", expand=True)


def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
