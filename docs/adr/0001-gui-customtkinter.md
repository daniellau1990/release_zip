# GUI 框架选型：CustomTkinter

为 zip_rar_tool 添加桌面 GUI 时，在 CustomTkinter、Gradio、PySide6 三个方案中选择
CustomTkinter。

**Considered Options**:
- **Gradio** — Web 界面，几行代码出 UI，但每次需启动 localhost 服务 + 浏览器，本地文件操
  作体验差（无原生文件对话框，拖拽受限），打包分发不友好。
- **PySide6** — 专业级桌面框架，功能全面，但体积大（~60MB+），学习曲线陡（Signal/Slot、
  QThread），三个函数的工具不需要这种重量级依赖。
- **CustomTkinter** — 基于 tkinter 的现代风格封装，轻量（pip install 即可），原生文件对话
  框，pyinstaller 打包为单个 .exe（~30-50MB），API 简单。

**Consequences**: 打包分发依赖 pyinstaller --onefile；拖拽功能需 tkinterdnd2 扩展（MVP 不做）；
主题跟随系统设置。
