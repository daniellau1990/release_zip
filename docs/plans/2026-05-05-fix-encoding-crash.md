# Fix Encoding Crash & Multi-file Compress Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Fix 4 bugs in multi-file compression: encoding corruption, .zip suffix, output path, and temp file pipeline

**Architecture:** Switch from `echo %files%|` pipe to temp file approach. Use `for %%f in (%files%)` loop in .bat to write each path to a temp file, Python reads with UTF-8 encoding.

**Tech Stack:** .bat, Python 3.10+, zipfile, py7zr

---

### Task 1: batch_compress.py rewrite

**Files:**
- Modify: `zip_rar_tool/batch_compress.py`

Changes:
- Accept temp file path as argv[2]
- Read from temp file with `encoding="utf-8"`
- Auto-append .zip when Path.suffix is empty
- Support both space and newline separated input

### Task 2: zip-rar-tool.bat COMPRESS rewrite

**Files:**
- Modify: `zip-rar-tool.bat`

Changes:
- `for %%f in (%files%) do @echo %%f > %TEMP%\zip_rar_files_%RANDOM%.txt`
- Pass temp file to Python
- Delete temp file after compression
- Prompt shows supported formats: `(supported: .zip, .7z, e.g. myarchive.zip)`

### Task 3: Update tests

**Files:**
- Modify: `tests/test_batch_compress.py`

- Update helper from stdin to temp file
- Add test_auto_suffix (input "a" → "a.zip")
- 6 test cases total

### Task 4: Run tests + save log

Run: `pytest tests/ -v`
Save: `docs/test-logs/2026-05-05-fix-encoding-crash.txt`

### Task 5: Commit

- Update Version.md (v0.1.2)
- git add + commit + tag v0.1.2
