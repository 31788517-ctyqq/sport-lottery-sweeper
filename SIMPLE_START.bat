@echo off
title Quick Start - Sport Lottery Sweeper

echo.
echo ================================================
echo   Starting Servers...
echo ================================================
echo.

REM Check if node_modules exists
if not exist "%~dp0frontend\node_modules" (
    echo ERROR: Frontend dependencies not installed!
    echo.
    echo Please run: INSTALL_AND_START.bat first
    echo.
    pause
    exit /b 1
)

echo Starting Backend...
start "Backend-8000" cmd /k "cd /d %~dp0 && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo Starting Frontend...
start "Frontend-5173" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ================================================
echo   Servers Started!
echo ================================================
echo.
echo Wait 30 seconds, then visit:
echo   http://localhost:5173/#/jczq-schedule
echo.
pause
