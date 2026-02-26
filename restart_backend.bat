@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo Stopping backend service (port 8000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo Terminating PID %%a ...
    taskkill /PID %%a /F >nul 2>&1
)

echo.
echo Waiting 3 seconds...
timeout /t 3 /nobreak >nul

echo.
echo Starting backend service...
start cmd /k "cd /d %~dp0 && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

echo.
echo Backend started. Check the new window for logs.
echo Access: http://localhost:8000

echo.
pause