@echo off
title 5G Network Slicing Simulator - NOC Server
color 0B
cls

echo =========================================================================
echo    5G NETWORK SLICING FOR SMART SERVICES - EXECUTABLE LAUNCHER
echo    Dynamic Resource Allocation, QoS Monitoring ^& Logical Slicing
echo =========================================================================
echo.

:: Detect Python executable
set "PYTHON_CMD="

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=python"
    goto :PYTHON_FOUND
)

where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set "PYTHON_CMD=py"
    goto :PYTHON_FOUND
)

if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
    goto :PYTHON_FOUND
)

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    goto :PYTHON_FOUND
)

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
    set "PYTHON_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    goto :PYTHON_FOUND
)

if exist "%ProgramFiles%\Python313\python.exe" (
    set "PYTHON_CMD=%ProgramFiles%\Python313\python.exe"
    goto :PYTHON_FOUND
)

echo [ERROR] Python 3 was not detected in PATH or standard installation directories.
echo Please install Python 3.8+ from https://www.python.org/
echo.
pause
exit /b 1

:PYTHON_FOUND
echo [*] Using Python interpreter: "%PYTHON_CMD%"
echo [*] Checking dependencies...
"%PYTHON_CMD%" -c "import flask" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [*] Installing required packages from requirements.txt...
    "%PYTHON_CMD%" -m pip install -r requirements.txt
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
)

echo.
echo =========================================================================
echo   [OK] Server initialized!
echo   [URL] http://127.0.0.1:5000
echo   [NOC] Opening your default web browser now...
echo =========================================================================
echo.

:: Launch browser in background after 2 seconds
start "" cmd /c "timeout /t 2 /nobreak >nul & start http://127.0.0.1:5000"

:: Start the Flask application
"%PYTHON_CMD%" app.py

echo.
echo Server stopped.
pause
