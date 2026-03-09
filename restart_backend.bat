@echo off
chcp 65001 >nul
setlocal

set "RELOAD_ARG="
if /i "%BACKEND_RELOAD%"=="1" set "RELOAD_ARG=-Reload"

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0restart_backend.ps1" -Port 8000 %RELOAD_ARG%

echo.
pause
