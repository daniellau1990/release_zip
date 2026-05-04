## ADDED Requirements

### Requirement: Interactive menu system
The system SHALL provide an interactive menu with options for extract, compress (multi-file), and list contents.

#### Scenario: Menu display on startup
- **WHEN** user double-clicks zip-rar-tool.bat
- **THEN** a menu with options 1-3 and 0 for exit is displayed

### Requirement: Drag-drop file path input
The system SHALL accept file paths by drag-drop into the cmd window.

#### Scenario: Drag archive for extraction
- **WHEN** user selects option 1 and drags a ZIP file into the window
- **THEN** the full path is captured and used as the archive path

### Requirement: Multi-file compression
The system SHALL accept multiple dragged files/folders and compress them into a single archive.

#### Scenario: Compress multiple files
- **WHEN** user selects option 2 and drags multiple files
- **THEN** all files are merged into one output archive

### Requirement: Default output paths
The system SHALL provide intelligent default output paths.

#### Scenario: Extract default output
- **WHEN** extracting C:\test.zip with empty output
- **THEN** output defaults to C:\test\

#### Scenario: Compress default output
- **WHEN** compressing with empty output name
- **THEN** output defaults to source folder name plus timestamp + .zip
