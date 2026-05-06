@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set "PY=%~dp0.venv\Scripts\python.exe"
if not exist "%~dp0logs\runs" mkdir "%~dp0logs\runs"
set "LOGDATE=%date%"
set "LOGDATE=%LOGDATE:/=-%"
set "LOGDATE=%LOGDATE: =_%"
set "LOGFILE=%~dp0logs\runs\run_log_%LOGDATE%.txt"
echo ===== %date% %time% ===== >> "%LOGFILE%"
echo [START] v0.2.2 >> "%LOGFILE%"

:MENU
cls
echo ======================================
echo    ZIP/RAR/7z Tool  v0.2.1
echo    Interactive Mode
echo ======================================
echo.
echo  1. Extract archive
echo  2. Compress (multi-file, one archive)
echo  3. List archive contents
echo  0. Exit
echo.
set /p "choice=Select [0-3]: "
echo [MENU] choice=%choice% >> "%LOGFILE%"

if "%choice%"=="1" goto EXTRACT
if "%choice%"=="2" goto COMPRESS
if "%choice%"=="3" goto LIST
if "%choice%"=="0" exit /b
goto MENU

:EXTRACT
cls
echo ===== Extract =====
set /p "archive=Archive path (drag file here): "
set "archive=%archive:"=%"
echo [EXTRACT] archive=%archive% >> "%LOGFILE%"
if not defined archive goto MENU
set /p "output=Output dir (Enter for default - archive name): "
if "%output%"=="" set "output=%~dpn1"
echo [EXTRACT] output=%output% >> "%LOGFILE%"
"%PY%" -m zip_rar_tool extract "%archive%" "%output%" >> "%LOGFILE%" 2>&1
echo [EXTRACT] done rc=%errorlevel% >> "%LOGFILE%"
echo.
pause
goto MENU

:COMPRESS
cls
echo ===== Compress (multi-file) =====
set "files="
set /p "files=Files/folders (select all, then drag here): "
set "files=%files:"=%"
echo [COMPRESS] raw input=%files% >> "%LOGFILE%"
if not defined files goto MENU

set "output="
set /p "output=Output filename (supported: .zip, .7z, e.g. myarchive.zip): "
if "%output%"=="" set "output=archive.zip"
echo [COMPRESS] output=%output% >> "%LOGFILE%"

set "tmpfile=%TEMP%\zip_rar_files_%RANDOM%.txt"
echo [COMPRESS] tmpfile=%tmpfile% >> "%LOGFILE%"
echo [COMPRESS] about_to_run_for_loop >> "%LOGFILE%"

REM Write each file path to temp file (one per line)
(for %%f in (%files%) do @echo %%f) > "%tmpfile%"
echo [COMPRESS] tmpfile content: >> "%LOGFILE%"
type "%tmpfile%" >> "%LOGFILE%" 2>&1
echo. >> "%LOGFILE%"

"%PY%" "%~dp0zip_rar_tool\batch_compress.py" "%output%" "%tmpfile%" >> "%LOGFILE%" 2>&1
echo [COMPRESS] done rc=%errorlevel% >> "%LOGFILE%"

if exist "%tmpfile%" del "%tmpfile%" 2>nul
echo.
pause
goto MENU

:LIST
cls
echo ===== List Contents =====
set /p "archive=Archive path (drag file here): "
set "archive=%archive:"=%"
echo [LIST] archive=%archive% >> "%LOGFILE%"
if "%archive%"=="" goto MENU
"%PY%" -m zip_rar_tool list "%archive%" >> "%LOGFILE%" 2>&1
echo [LIST] done >> "%LOGFILE%"
echo.
pause
goto MENU
