# Version History

## 版本映射

| Version | Git Tag | Commit | Date |
|---------|:-------:|:------:|:----:|
| v0.1.1  | 0.1.1 | 2543dbf | 2026-05-04 |
| v0.1.0  | 0.1.0 | 6688038 | 2026-05-04 |

---

## v0.1.1 (2026-05-04) 	ag: v0.1.1

- Fix: multi-file compress crash when dragging into .bat (stdin + shlex)
- Add: tests/test_batch_compress.py (5 test cases)
- Change: batch_compress.py reads from stdin instead of sys.argv

---

## v0.1.0 (2026-05-04) 	ag: v0.1.0 commit: 6688038

- Initial release: ZIP/RAR/7z extract, compress, list
- Interactive .bat menu with drag-drop support
- Multi-file compression (option B)
- Three-tier defense system (AGENTS.md hooks + plugin + pre-commit)
- CLI: extract/list/compress commands
## v0.1.2 (2026-05-05) 	ag: v0.1.2

- Fix: Chinese path encoding (temp file instead of echo pipe)
- Fix: auto-append ".zip" when output has no suffix
- Fix: multi-file drag-drop via for loop in .bat
- Add: test_logs/ directory for test output retention
- Add: 5 batch_compress tests (single, multi, folder, auto-suffix, quoted)

## v0.1.3 (2026-05-05) 	ag: v0.1.3`r

- Fix: output path now uses user's working directory (not project dir)
- Fix: drag-drop concatenated paths "quoted"adjacent parsed correctly
- Change: regex instead of shlex.split for Windows path parsing

## v0.1.4 (2026-05-05) 	ag: v0.1.4 commit: HEAD`r

- Fix: output auto-saves to first input file's directory (even if .bat runs elsewhere)