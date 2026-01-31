@echo off
chcp 65001 >nul
echo ========================================
echo      体育彩票扫盘系统 - 一键启动
echo ========================================
echo 前端端口: 3000
echo 后端端口: 8000
echo ========================================
echo.

:: 检查端口占用
netstat -ano | findstr :3000 >nul 2>nul
if %errorlevel% equ 0 (
    echo ⚠️  端口3000已被占用，正在停止相关进程...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do taskkill /f /pid %%a >nul 2>nul
    timeout /t 2 /nobreak >nul
)

netstat -ano | findstr :8000 >nul 2>nul
if %errorlevel% equ 0 (
    echo ⚠️  端口8000已被占用，正在停止相关进程...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do taskkill /f /pid %%a >nul 2>nul
    timeout /t 2 /nobreak >nul
)

echo.
echo 🚀 启动后端服务 (端口8000)...
start "Backend Service" cmd /k "cd backend && python start_server.py"

echo ⏳ 等待后端服务启动...
timeout /t 5 /nobreak >nul

echo.
echo 🚀 启动前端服务 (端口3000)...
start "Frontend Service" cmd /k "cd frontend && npm run dev"

echo.
echo ✅ 服务启动完成！
echo.
echo 📱 前端访问地址: http://localhost:3000
echo 🔧 后端API地址: http://localhost:8000
echo 📖 API文档: http://localhost:8000/docs
echo ❤️  健康检查: http://localhost:8000/health/live
echo.
echo 按任意键关闭此窗口...
pause >nul