@echo off
echo ========================================
echo Checking Frontend Status
echo ========================================
echo.

echo Checking if Node.js is running...
tasklist | findstr node.exe
echo.

echo Checking port 5173...
netstat -ano | findstr ":5173"
echo.

echo Testing HTTP connection...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:5173/' -TimeoutSec 3 -UseBasicParsing; Write-Host 'SUCCESS! Frontend is accessible'; Write-Host 'Status Code:', $response.StatusCode } catch { Write-Host 'Not accessible yet:', $_.Exception.Message }"
echo.

echo ========================================
echo Done!
echo ========================================
pause
