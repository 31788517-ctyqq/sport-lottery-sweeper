@echo off
echo 正在停止后端服务...
taskkill /f /im uvicorn.exe 2>nul
taskkill /f /im python.exe 2>nul

echo.
echo 等待几秒让进程完全终止...
timeout /t 3 /nobreak >nul

echo.
echo 正在启动后端服务...
start cmd /k "cd /d %~dp0 && python -m uvicorn backend.main:app --host 0.0.0.0 --port 3000 --reload"

echo.
echo 服务已在新窗口中启动，请检查新窗口确认服务运行状态。
echo 您现在可以在浏览器中访问 http://localhost:3000 查看服务状态。