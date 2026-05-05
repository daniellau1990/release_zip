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