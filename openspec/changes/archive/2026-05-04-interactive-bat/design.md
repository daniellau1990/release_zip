## Context

Current zip-rar-tool.bat is single-line pass-through. Need interactive menu with drag-drop support.

## Goals / Non-Goals

**Goals:**
- Interactive menu loop (extract/compress/list) until user exits
- Drag-drop support for file paths
- Default output = archive name without extension
- Multi-file compression merged into one archive
- All changes via .bat + helper script, no backend changes

**Non-Goals:**
- No GUI
- No changes to zip_rar_tool/ core library
- No RAR compression

## Decisions

- Language: pure .bat + Python helper script
- Multi-file compress: new batch_compress.py using zipfile/py7zr directly
- Menu: set /p + goto label, compatible with all Windows
- Encoding: chcp 65001 for UTF-8 display

## Risks

- Spaces in paths: quote all path variables
- Python path with Chinese: already verified working
