@echo off
cd /d %~dp0frontend
echo Starting Frontend Server on port 5173...
npm run dev
pause
