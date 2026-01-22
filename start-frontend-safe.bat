@echo off
setlocal enabledelayedexpansion

cd /d "%~dp0"

echo Starting frontend...
echo Current directory: %CD%

cd frontend

if not exist package.json (
    echo ERROR: package.json not found in frontend directory!
    dir
    pause
    exit /b 1
)

echo Checking dependencies...

if not exist node_modules (
    echo Installing dependencies with pnpm...
    call pnpm install
    if errorlevel 1 (
        echo Failed to install dependencies
        pause
        exit /b 1
    )
)

echo Starting development server...
echo Frontend will run at: http://localhost:3000
echo Press Ctrl+C to stop
echo.

call pnpm run dev

pause
