@echo off
chcp 65001 >nul
echo.
echo ========================================
echo Restarting Backend Server
echo ========================================
echo.

echo Step 1: Stopping old backend process...
taskkill /F /FI "WINDOWTITLE eq Backend*" 2>nul
powershell -Command "Get-Process | Where-Object {$_.ProcessName -eq 'python'} | ForEach-Object { $ports = Get-NetTCPConnection -OwningProcess $_.Id -ErrorAction SilentlyContinue | Where-Object {$_.LocalPort -eq 8000}; if ($ports) { Write-Host 'Killing process' $_.Id; Stop-Process -Id $_.Id -Force } }"
timeout /t 2 /nobreak >nul

echo.
echo Step 2: Starting new backend process...
cd /d "%~dp0"
start "Backend Server" python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

echo.
echo ========================================
echo Backend is starting...
echo Wait 10 seconds for it to fully start
echo ========================================
echo.
timeout /t 10 /nobreak

echo.
echo Testing API...
powershell -Command "try { $r = Invoke-RestMethod 'http://localhost:8000/api/v1/jczq/matches?source=500'; Write-Host ('Success! Total matches: ' + $r.total) } catch { Write-Host 'API not ready yet, please wait...' }"

echo.
echo ========================================
echo Done! Backend should be running on:
echo http://localhost:8000
echo ========================================
echo.
pause
