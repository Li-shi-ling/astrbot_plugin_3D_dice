@echo off
setlocal EnableExtensions
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PLUGIN_DIR=%%~fI"
set "OUTPUT_DIR=%SCRIPT_DIR%outputs"

set "PYTHON_EXE="
if exist "%PLUGIN_DIR%\..\..\..\.venv\Scripts\python.exe" (
    for %%I in ("%PLUGIN_DIR%\..\..\..\.venv\Scripts\python.exe") do set "PYTHON_EXE=%%~fI"
)
if not defined PYTHON_EXE if exist "%PLUGIN_DIR%\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%PLUGIN_DIR%\.venv\Scripts\python.exe"
)
if not defined PYTHON_EXE set "PYTHON_EXE=python"

if not exist "%OUTPUT_DIR%" mkdir "%OUTPUT_DIR%"

set "DICE_PLUGIN_DIR=%PLUGIN_DIR%"
set "DICE_OUTPUT_DIR=%OUTPUT_DIR%"

echo Plugin: %DICE_PLUGIN_DIR%
echo Output: %DICE_OUTPUT_DIR%
echo Python: %PYTHON_EXE%
echo.

"%PYTHON_EXE%" "%SCRIPT_DIR%generate_dice_styles.py"
if errorlevel 1 (
    echo.
    echo Failed to generate GIFs. Check the error above.
    pause
    exit /b 1
)

echo.
echo Done. Open: %OUTPUT_DIR%
pause
