@echo off
chcp 65001 >nul
echo ==========================================
echo  Start Frontend Dev Server (Safe Mode)
echo ==========================================

set FRONTEND_DIR=c:\Users\11581\Downloads\sport-lottery-sweeper\frontend

echo Entering frontend directory %FRONTEND_DIR%
cd /d "%FRONTEND_DIR%"
if errorlevel 1 (
    echo [ERROR] Directory not found: %FRONTEND_DIR%
    pause
    exit /b
)

echo Installing dependencies if not exist...
if not exist node_modules (
    echo Installing...
    npm install
)

echo Starting frontend dev server...
start "FrontendDev" cmd /k "npm run dev"

echo Waiting 10 seconds for frontend to start...
timeout /t 10 >nul

echo Please open browser and visit:
echo   http://localhost:5173/admin/login
echo   or http://localhost:5174/admin/login
echo   or http://localhost:3000/admin/login
pause