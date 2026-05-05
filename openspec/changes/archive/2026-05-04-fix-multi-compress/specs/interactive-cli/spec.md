## MODIFIED Requirements

### Requirement: Multi-file compression
The system SHALL accept multiple dragged files/folders via stdin pipe and compress them into a single archive.

#### Scenario: Compress multiple files with special characters in path
- **WHEN** paths contain `&`, `^`, `%`, or Chinese characters
- **THEN** compression succeeds without cmd crash
