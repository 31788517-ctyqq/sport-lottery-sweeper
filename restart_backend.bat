@echo off
cd /d c:\Users\11581\Downloads\sport-lottery-sweeper\backend

echo Stopping existing service...
taskkill /F /IM python.exe 2>nul

timeout /t 2 /nobreak >nul

echo Starting backend service...
python main.py > backend.log 2>&1

timeout /t 5 /nobreak >nul

echo Checking service status...
curl -s "http://localhost:8000/health/live"

echo.
echo Done!
pause
