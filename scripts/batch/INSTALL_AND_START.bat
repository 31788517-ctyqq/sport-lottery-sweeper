@echo off
title Installing and Starting Servers

echo ================================================
echo   Step 1: Installing Frontend Dependencies
echo ================================================
echo.
echo This may take 2-5 minutes...
echo.

cd /d %~dp0frontend

echo Checking for npm...
where npm >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: npm is not installed!
    echo Please install Node.js from: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

echo Installing dependencies with npm...
call npm install

if %errorlevel% neq 0 (
    echo.
    echo ERROR: npm install failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ================================================
echo   Step 2: Starting Backend Server
echo ================================================
echo.

cd /d %~dp0

start "Backend-8000" cmd /k "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak >nul

echo.
echo ================================================
echo   Step 3: Starting Frontend Server
echo ================================================
echo.

cd /d %~dp0frontend
start "Frontend-5173" cmd /k "npm run dev"

echo.
echo ================================================
echo   All Done!
echo ================================================
echo.
echo Two server windows have opened:
echo   1. Backend Server - Port 8000
echo   2. Frontend Server - Port 5173
echo.
echo Wait 30 seconds, then visit:
echo   http://localhost:5173/#/jczq-schedule
echo.
echo You should see Monday's 5 matches!
echo.
echo Press any key to close this window...
pause >nul
