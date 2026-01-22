@echo off
cd /d "%~dp0frontend"
echo ====================================
echo Starting Frontend Server
echo ====================================
echo.
echo Frontend will run at: http://localhost:3000
echo Press Ctrl+C to stop the server
echo.
powershell -Command "C:\Users\11581\AppData\Roaming\npm\pnpm.cmd run dev"
pause
