@echo off
setlocal EnableExtensions
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PLUGIN_DIR=%%~fI"
set "BENCH_OUTPUT_DIR=%SCRIPT_DIR%benchmarks"

set "PYTHON_EXE="
if exist "%PLUGIN_DIR%\..\..\..\.venv\Scripts\python.exe" (
    for %%I in ("%PLUGIN_DIR%\..\..\..\.venv\Scripts\python.exe") do set "PYTHON_EXE=%%~fI"
)
if not defined PYTHON_EXE if exist "%PLUGIN_DIR%\.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%PLUGIN_DIR%\.venv\Scripts\python.exe"
)
if not defined PYTHON_EXE set "PYTHON_EXE=python"

if not exist "%BENCH_OUTPUT_DIR%" mkdir "%BENCH_OUTPUT_DIR%"

set "DICE_PLUGIN_DIR=%PLUGIN_DIR%"
set "DICE_BENCH_OUTPUT_DIR=%BENCH_OUTPUT_DIR%"

rem Optional overrides:
rem set "DICE_BENCH_DICE=D4,D6,D8,D10,D20"
rem set "DICE_BENCH_COUNTS=1,2,3,4,5,6"
rem set "DICE_BENCH_WIDTH=840"
rem set "DICE_BENCH_HEIGHT=600"
rem set "DICE_BENCH_FPS=12"
rem set "DICE_BENCH_DURATION_MS=5000"
rem set "DICE_BENCH_FINAL_HOLD_MS=3000"
rem set "DICE_BENCH_SAVE_GIFS=1"

echo Plugin: %DICE_PLUGIN_DIR%
echo Output: %DICE_BENCH_OUTPUT_DIR%
echo Python: %PYTHON_EXE%
echo.

"%PYTHON_EXE%" "%SCRIPT_DIR%benchmark_dice_render.py"
if errorlevel 1 (
    echo.
    echo Benchmark failed or had failed jobs. Check the report above.
    pause
    exit /b 1
)

echo.
echo Done. Open: %DICE_BENCH_OUTPUT_DIR%
pause
