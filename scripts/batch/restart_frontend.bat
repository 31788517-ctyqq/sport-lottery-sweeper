@echo off
chcp 65001 >nul
echo.
echo ========================================
echo Restarting Frontend
echo ========================================
echo.

echo Stopping frontend...
powershell -Command "Get-Process node -ErrorAction SilentlyContinue | Where-Object { (Get-NetTCPConnection -OwningProcess $_.Id -ErrorAction SilentlyContinue | Where-Object {$_.LocalPort -ge 3000 -and $_.LocalPort -le 3010}).Count -gt 0 } | ForEach-Object { Stop-Process -Id $_.Id -Force }"
timeout /t 2 /nobreak >nul

echo.
echo Starting frontend...
cd /d "%~dp0\frontend"
start "Frontend Server" npm run dev

echo.
echo ========================================
echo Frontend is starting...
echo Check the new window for the port number
echo ========================================
echo.
pause
