## Context

Current `batch_compress.py` receives file paths via `sys.argv`. When called from `.bat`, the `%files%` variable is expanded unquoted, causing cmd.exe to misinterpret paths with special characters. Result: cmd crashes, window closes.

## Goals / Non-Goals

**Goals:**
- Fix cmd crash when dragging multiple files
- Preserve backward compatibility for single-file and programmatic use
- Add proper test coverage

**Non-Goals:**
- No changes to extract/list logic
- No changes to backend/core modules

## Decisions

- **Input method**: Switch from `sys.argv` to `stdin` + `shlex.split()`. This bypasses cmd.exe argument parsing entirely. The .bat pipes the input via `echo`.
- **shlex.split()**: Handles both quoted and unquoted paths, respects spaces, ignores cmd special characters.
- **Output path**: Passed as the last argument (unchanged), but now via argv[1] instead of argv[-1].

## Risks

- **[Low] Existing callers**: Only the .bat calls this module, and we're updating the .bat too.
- **[Low] shlex availability**: stdlib module, always available.
