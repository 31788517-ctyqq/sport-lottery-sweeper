@echo off
title Fix and Install Frontend

echo ================================================
echo   Fixing and Installing Frontend
echo ================================================
echo.

cd /d %~dp0frontend

echo Step 1: Cleaning npm cache...
call npm cache clean --force
echo.

echo Step 2: Removing old files...
if exist node_modules rmdir /s /q node_modules
if exist package-lock.json del package-lock.json
echo.

echo Step 3: Installing dependencies...
echo This will take 2-5 minutes, please wait...
echo.
call npm install --legacy-peer-deps
echo.

if %errorlevel% equ 0 (
    echo ================================================
    echo   Installation Successful!
    echo ================================================
    echo.
    echo Now starting servers...
    echo.
    
    cd /d %~dp0
    
    echo Starting Backend...
    start "Backend-8000" cmd /k "python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"
    
    timeout /t 3 /nobreak >nul
    
    echo Starting Frontend...
    start "Frontend-5173" cmd /k "cd /d %~dp0frontend && npm run dev"
    
    echo.
    echo ================================================
    echo   All Done!
    echo ================================================
    echo.
    echo Wait 30 seconds, then visit:
    echo   http://localhost:5173/#/jczq-schedule
    echo.
) else (
    echo ================================================
    echo   Installation Failed!
    echo ================================================
    echo.
    echo Please check the error messages above.
    echo.
)

pause
