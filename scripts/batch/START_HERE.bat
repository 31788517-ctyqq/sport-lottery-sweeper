@echo off
title Sport Lottery Sweeper - Quick Start

echo.
echo ================================================
echo   Sport Lottery Sweeper - Quick Start
echo ================================================
echo.
echo This will start both Backend and Frontend servers
echo.
echo Backend will run on: http://localhost:8000
echo Frontend will run on: http://localhost:5173
echo.
echo Press any key to start...
pause >nul

echo.
echo Starting Backend Server...
start "Backend-8000" cmd /c "cd /d %~dp0 && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 3 /nobreak >nul

echo Starting Frontend Server...
start "Frontend-5173" cmd /c "cd /d %~dp0frontend && npm run dev"

echo.
echo ================================================
echo   Servers Started!
echo ================================================
echo.
echo Two new windows have opened:
echo   1. Backend Server (port 8000)
echo   2. Frontend Server (port 5173)
echo.
echo Wait 30 seconds, then open your browser:
echo   http://localhost:5173/#/jczq-schedule
echo.
echo Press any key to exit this window...
pause >nul
