## MODIFIED Requirements

### Requirement: Multi-file compression with Chinese paths
The system SHALL handle file paths containing Chinese characters and spaces without encoding corruption.

#### Scenario: Chinese path without quotes
- **WHEN** user enters `C:\用户\文档\文件.txt` as a file path
- **THEN** compression succeeds, file is found and added to archive

#### Scenario: Output filename ".zip" only
- **WHEN** user enters `.zip` as output filename
- **THEN** system treats it as valid .zip extension and creates archive
