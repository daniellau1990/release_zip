# Interactive .bat Implementation Plan

**Goal:** Rewrite zip-rar-tool.bat to interactive menu with drag-drop support

**Architecture:** Pure .bat menu loop + Python helper for multi-file compression

**Tech Stack:** .bat, Python 3.10+, zipfile, py7zr, rarfile

---

### Task 1: Rewrite zip-rar-tool.bat with menu loop

**Files:**
- Modify: zip-rar-tool.bat

Key structure:
- :MENU label loop with cls
- set /p for menu selection and file paths
- All paths quoted for spaces

Menu: 1=Extract, 2=Compress, 3=List, 0=Exit

---

### Task 2: Implement extract in .bat

- Prompt for archive path (drag-drop)
- Default output = archive name without extension
- Call: python -m zip_rar_tool extract

---

### Task 3: Implement list in .bat

- Prompt for archive path
- Call: python -m zip_rar_tool list

---

### Task 4: Multi-file compress

**Files:**
- Create: zip_rar_tool/batch_compress.py
- Modify: zip-rar-tool.bat

batch_compress.py accepts sources + output path.
Uses zipfile for .zip, py7zr for .7z.

---

### Task 5: Test

- Extract .zip/.rar/.7z
- Compress single + multiple files
- List contents
- Menu return/exit loop