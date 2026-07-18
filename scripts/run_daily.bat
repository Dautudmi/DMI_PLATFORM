@echo off
setlocal EnableExtensions

rem ==================================================
rem DMI Platform - Daily Production Launcher
rem ==================================================

set "SCRIPT_DIR=%~dp0"
for %%I in ("%SCRIPT_DIR%..") do set "PROJECT_ROOT=%%~fI"

set "PYTHON_COMMAND=python"
set "PYTHON_SCRIPT=%PROJECT_ROOT%\scripts\run_daily.py"

set "SCHEDULER_LOG_DIR=%PROJECT_ROOT%\logs\scheduler"
set "SCHEDULER_LOG_FILE=%SCHEDULER_LOG_DIR%\scheduler.log"

if not exist "%SCHEDULER_LOG_DIR%" (
    mkdir "%SCHEDULER_LOG_DIR%"
)

echo.>> "%SCHEDULER_LOG_FILE%"
echo ==================================================>> "%SCHEDULER_LOG_FILE%"
echo [%date% %time%] DMI scheduler launcher started>> "%SCHEDULER_LOG_FILE%"
echo Project root: %PROJECT_ROOT%>> "%SCHEDULER_LOG_FILE%"

cd /d "%PROJECT_ROOT%"

if not exist "%PYTHON_SCRIPT%" (
    echo [%date% %time%] ERROR: Python script not found: %PYTHON_SCRIPT%>> "%SCHEDULER_LOG_FILE%"
    echo [%date% %time%] Launcher exit code: 50>> "%SCHEDULER_LOG_FILE%"
    exit /b 50
)

where %PYTHON_COMMAND% >nul 2>&1

if errorlevel 1 (
    echo [%date% %time%] ERROR: Python command not found>> "%SCHEDULER_LOG_FILE%"
    echo [%date% %time%] Launcher exit code: 51>> "%SCHEDULER_LOG_FILE%"
    exit /b 51
)

%PYTHON_COMMAND% "%PYTHON_SCRIPT%" >> "%SCHEDULER_LOG_FILE%" 2>&1

set "DMI_EXIT_CODE=%ERRORLEVEL%"

echo [%date% %time%] DMI runtime exit code: %DMI_EXIT_CODE%>> "%SCHEDULER_LOG_FILE%"
echo [%date% %time%] DMI scheduler launcher completed>> "%SCHEDULER_LOG_FILE%"
echo ==================================================>> "%SCHEDULER_LOG_FILE%"

exit /b %DMI_EXIT_CODE%