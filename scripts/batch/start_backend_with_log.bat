@echo off
cd /d %~dp0
echo ============================================
echo 启动后端服务器
echo ============================================
echo.
echo 项目路径: %CD%
echo Python: 
python --version
echo.
echo 开始启动 Uvicorn...
echo ============================================
echo.

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload 2>&1

echo.
echo ============================================
echo 服务器已停止
echo ============================================
pause
