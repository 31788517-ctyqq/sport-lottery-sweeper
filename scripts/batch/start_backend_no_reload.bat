@echo off
cd /d %~dp0
echo Starting Backend Server on port 8000 (no reload mode)...
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
echo Server stopped.
pause
