@echo off
cd /d %~dp0
echo Checking for existing backend processes...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Backend Server" 2>nul || echo No existing backend processes found.

echo Starting Backend Server on port 8002...
start "Backend Server" python -m uvicorn backend.main:app --host 0.0.0.0 --port 8002
echo Server started on port 8002.
echo Press any key to stop the server...
pause

taskkill /F /IM python.exe /FI "WINDOWTITLE eq Backend Server"
echo Server stopped.
