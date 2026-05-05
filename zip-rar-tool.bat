@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

:MENU
cls
echo ======================================
echo    ZIP/RAR/7z Tool  v0.1.0
echo    Interactive Mode
echo ======================================
echo.
echo  1. Extract archive
echo  2. Compress (multi-file, one archive)
echo  3. List archive contents
echo  0. Exit
echo.
set /p "choice=Select [0-3]: "

if "%choice%"=="1" goto EXTRACT
if "%choice%"=="2" goto COMPRESS
if "%choice%"=="3" goto LIST
if "%choice%"=="0" exit /b
goto MENU

:EXTRACT
cls
echo ===== Extract =====
set /p "archive=Archive path (drag file here): "
if "%archive%"=="" goto MENU

set "outdir=%~dpn1"
set /p "output=Output dir (Enter for default): "
if "%output%"=="" set "output=%outdir%"

.venv\Scripts\python.exe -m zip_rar_tool extract "%archive%" "%output%"
echo.
pause
goto MENU

:COMPRESS
cls
echo ===== Compress (multi-file) =====
set "files="
set /p "files=Files/folders (drag here, space separated): "
if "%files%"=="" goto MENU

set /p "output=Output filename (Enter for archive.zip): "
if "%output%"=="" set "output=archive.zip"

echo %files%| .venv\Scripts\python.exe -m zip_rar_tool.batch_compress "%output%"
echo.
pause
goto MENU

:LIST
cls
echo ===== List Contents =====
set /p "archive=Archive path (drag file here): "
if "%archive%"=="" goto MENU

.venv\Scripts\python.exe -m zip_rar_tool list "%archive%"
echo.
pause
goto MENU