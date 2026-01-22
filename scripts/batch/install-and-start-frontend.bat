@echo off
cd /d "%~dp0frontend"
echo Installing frontend dependencies...
pnpm install
if errorlevel 1 (
    echo Installation failed!
    pause
    exit /b 1
)
echo Starting frontend server...
pnpm run dev
pause
