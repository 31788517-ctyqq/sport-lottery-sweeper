@echo off
echo ========================================
echo Starting Backend and Frontend Servers
echo ========================================
echo.

echo [1/2] Starting Backend Server...
echo.
start "Backend Server" cmd /k "cd /d %~dp0 && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

echo Waiting 3 seconds...
timeout /t 3 /nobreak >nul

echo.
echo [2/2] Starting Frontend Server...
echo.
start "Frontend Server" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ========================================
echo Servers are starting...
echo ========================================
echo.
echo Please wait 30 seconds for servers to fully start
echo.
echo Then visit: http://localhost:5173/#/jczq-schedule
echo.
echo Servers:
echo    - Backend: http://localhost:8000
echo    - Frontend: http://localhost:5173
echo    - API Docs: http://localhost:8000/docs
echo.
echo Press any key to close this window...
pause >nul
