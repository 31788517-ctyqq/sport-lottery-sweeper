@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ========================================
echo     Restart Frontend Service Script
echo ========================================

:: Function: Kill process on specified port
:kill_port
    set port=%1
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%port% ^| findstr LISTENING') do (
        echo Terminating process occupying port %port% PID=%%a ...
        taskkill /PID %%a /F >nul 2>&1
    )
    exit /b

:: Stop existing frontend service
echo Stopping existing frontend service...
call :kill_port 3000

echo Waiting 2 seconds...
timeout /t 2 /nobreak >nul

:: Start frontend service
echo Starting frontend service...
cd /d "%~dp0\frontend"

if exist "%~dp0\frontend\package.json" (
    echo Checking dependencies...
    if not exist "%~dp0\frontend\node_modules" (
        echo Installing dependencies...
        pnpm install
    )
    echo Starting frontend development server...
    start "Frontend" /min cmd /c "pnpm run dev & pause"
    echo ========================================
    echo       Frontend service started!
    echo ========================================
    echo Access address: http://localhost:3000
    echo Note: Access the above address to view the frontend application.
) else (
    echo Error: Frontend configuration file frontend\package.json not found
    pause
    exit /b
)

pause