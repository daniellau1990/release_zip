## Why

Current zip-rar-tool.bat is a single-line pass-through. Users must type full commands manually. Need an interactive menu with drag-drop support.

## What Changes

- Rewrite zip-rar-tool.bat: from single-line to interactive menu loop
- Add zip_rar_tool/batch_compress.py: multi-file merge compression helper
- Support three operations: extract, multi-file compress, list contents
- All operations support drag-drop file paths
- Default output path = archive name without extension (for extract)
- Multi-file compression merges all sources into one archive

## Capabilities

### New Capabilities

- interactive-cli: Interactive command-line interface with menu selection and drag-drop support

### Modified Capabilities

- None (new project, no existing specs)

## Impact

- zip-rar-tool.bat: rewritten
- zip_rar_tool/batch_compress.py: new file
- No impact on existing backend or core logic
