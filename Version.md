# Version History

## 版本映射

| Version | Git Tag | Commit | Time (UTC+8) |
|---------|:-------:|:------:|--------------|
| v0.2.2  | v0.2.2 | 30c4972 | 2026-05-06 18:43:33 |
| v0.2.1  | v0.2.1 | 3d573a1 | 2026-05-06 18:26:39 |
| v0.2.0  | v0.2.0 | 055e579 | 2026-05-06 14:33:19 |
| v0.1.4  | v0.1.4 | ad9974e | 2026-05-06 00:38:51 |
| v0.1.3  | v0.1.3 | 6103e72 | 2026-05-05 20:01:47 |
| v0.1.2  | v0.1.2 | 952c58a | 2026-05-05 19:22:25 |
| v0.1.1  | v0.1.1 | 8dc2aad | 2026-05-05 12:22:57 |
| v0.1.0  | v0.1.0 | 6688038 | 2026-05-04 23:01:48 |

---

## v0.2.2 (2026-05-06 18:43:33) tag: v0.2.2 commit: 30c4972

- Fix: strip drag-drop `"` from archive/files after set /p
- Fix: use full %date% instead of truncated ~0,10 for LOGFILE filename
- Root cause: drag-drop quotes cause CMD double-quoting -> Typer arg count mismatch

---

## v0.2.1 (2026-05-06 18:26:39) tag: v0.2.1 commit: 3d573a1

- Fix: Chinese locale %date% slash breaks LOGFILE path, prevents all commands from running
- Fix: add mkdir logs/runs/ defense before first log write
- Root cause: %date% = 2026/05/06, / interpreted as dir separator in CMD redirect

---

## v0.1.1 (2026-05-05 12:22:57) tag: v0.1.1 commit: 8dc2aad

- Fix: multi-file compress crash when dragging into .bat (stdin + shlex)
- Add: tests/test_batch_compress.py (5 test cases)
- Change: batch_compress.py reads from stdin instead of sys.argv

---

## v0.1.0 (2026-05-04 23:01:48) tag: v0.1.0 commit: 6688038

- Initial release: ZIP/RAR/7z extract, compress, list
- Interactive .bat menu with drag-drop support
- Multi-file compression (option B)
- Three-tier defense system (AGENTS.md hooks + plugin + pre-commit)
- CLI: extract/list/compress commands
## v0.1.2 (2026-05-05 19:22:25) tag: v0.1.2 commit: 952c58a

- Fix: Chinese path encoding (temp file instead of echo pipe)
- Fix: auto-append ".zip" when output has no suffix
- Fix: multi-file drag-drop via for loop in .bat
- Add: test_logs/ directory for test output retention
- Add: 5 batch_compress tests (single, multi, folder, auto-suffix, quoted)

## v0.1.3 (2026-05-05 20:01:47) tag: v0.1.3 commit: 6103e72

- Fix: output path now uses user's working directory (not project dir)
- Fix: drag-drop concatenated paths "quoted"adjacent parsed correctly
- Change: regex instead of shlex.split for Windows path parsing

## v0.1.4 (2026-05-06 00:38:51) tag: v0.1.4 commit: ad9974e

- Fix: output auto-saves to first input file's directory (even if .bat runs elsewhere)

## v0.2.0 (2026-05-06 14:33:19) tag: v0.2.0 commit: 055e579

- **BREAKING FIX**: if defined instead of quoted if (cmd crash from drag-drop quotes)
- Add: run_log.txt >> append mode (never overwrite old logs)
- Add: debugging 5-whys principle to AGENTS.md