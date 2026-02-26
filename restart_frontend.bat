@echo off
chcp 65001 >nul
setlocal

echo ========================================
echo     Restart Frontend Service Script
echo ========================================

call :kill_port 3000

echo Waiting 2 seconds...
timeout /t 2 /nobreak >nul

:: Verify port 3000 is free
netstat -ano | findstr :3000 | findstr LISTENING >nul
if %errorlevel% equ 0 (
    echo Port 3000 is still in use. Please close it and retry.
    pause
    exit /b 1
)

:: Start frontend service
echo Starting frontend service...
cd /d "%~dp0\frontend"

if exist "%~dp0\frontend\package.json" (
    echo Checking dependencies...
    if not exist "%~dp0\frontend\node_modules" (
        echo Installing dependencies...
        npm install
    )
    echo Starting frontend development server...
    start "Frontend" /min cmd /c "npm run dev -- --host 0.0.0.0 --port 3000 & pause"
    echo ========================================
    echo       Frontend service started!
    echo ========================================
    echo Access address: http://localhost:3000
    echo Note: Access the above address to view the frontend application.
    start "" "http://localhost:3000"
) else (
    echo Error: Frontend configuration file frontend\package.json not found
    pause
    exit /b
)

pause
exit /b 0

:kill_port
set "PORT=%~1"
echo Checking port %PORT%...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%PORT% ^| findstr LISTENING') do (
    for /f "tokens=1" %%p in ('tasklist /fi "PID eq %%a" /nh') do (
        if /i "%%p"=="node.exe" (
            echo Terminating node process PID=%%a ...
            taskkill /PID %%a /F >nul 2>&1
        ) else (
            echo Skip PID=%%a (%%p)
        )
    )
)
exit /b
