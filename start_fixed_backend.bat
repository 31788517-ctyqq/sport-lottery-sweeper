@echo off
chcp 65001 >nul
echo ========================================
echo 🚀 体育彩票扫盘系统 - 修复版后端服务
echo ========================================
echo.

:: 检查是否已有 Python 进程在运行
netstat -ano | findstr :8000 >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  检测到端口 8000 已被占用
    echo 正在停止现有的 Python 进程...
    taskkill /f /im python.exe >nul 2>&1
    timeout /t 2 /nobreak >nul
)

echo 📂 切换到项目目录...
cd /d c:\Users\11581\Downloads\sport-lottery-sweeper\backend

echo.
echo 🔧 启动修复版后端服务...
echo 服务地址: http://localhost:8000
echo API文档:  http://localhost:8000/docs
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

:: 启动后端服务
python main.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ 服务启动失败，请检查错误信息
    pause
)

echo.
echo 👋 服务已停止
echo ========================================
pause