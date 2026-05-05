## 1. Fix output path and encoding

- [ ] 1.1 batch_compress.py: Handle `.zip` suffix + auto-append `.zip` when no suffix
- [ ] 1.2 zip-rar-tool.bat: Change COMPRESS to write temp file instead of echo pipe
- [ ] 1.3 zip-rar-tool.bat: Update prompt to show supported formats
- [ ] 1.4 zip-rar-tool.bat: Fix output path to user's working directory

## 2. Add tests + logs

- [ ] 2.1 Write test for `.zip` output + auto-suffix
- [ ] 2.2 Write test for Chinese path via temp file
- [ ] 2.3 Save test log to docs/test-logs/2026-05-05-fix-encoding-crash.txt

## 3. Commit

- [ ] 3.1 git add + commit + update Version.md
- [ ] 3.2 git tag v0.1.2
