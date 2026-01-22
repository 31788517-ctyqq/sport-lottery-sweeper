@echo off
chcp 65001 > nul
cd /d %~dp0

echo ========================================
echo 启动后端服务器（测试模式）
echo ========================================
echo.

echo 🚀 启动 FastAPI 后端...
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

pause
