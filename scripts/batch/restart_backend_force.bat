@echo off
chcp 65001 >nul
echo ========================================
echo 强制重启后端服务 - 解决数据库配置问题
echo ========================================
echo.
:: 防止闪退，出错时暂停
if not exist "backend" (
    echo 错误: 找不到 backend 目录
    pause
    exit /b 1
)

cd /d "%~dp0"

:: 停止所有Python进程
echo [1/3] 强制停止所有Python进程...
taskkill /f /im python.exe >nul 2>&1
echo 等待2秒确保进程完全停止...
timeout /t 2 /nobreak >nul
echo.

:: 启动后端服务
echo [2/3] 启动后端服务...
cd backend
echo 使用SQLite数据库: sport_lottery.db
start "Backend Service" cmd /k "python main.py"
echo 后端服务启动中，请等待15秒...
timeout /t 15 /nobreak >nul
echo.

:: 测试API
echo [3/3] 测试API...
cd ..
echo 测试健康检查...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ 后端服务正常启动
    echo.
    echo 测试用户管理API...
    curl -s http://localhost:8000/api/v1/admin-users/
) else (
    echo ✗ 后端服务启动异常
    echo 请检查后端日志
)

echo.
echo ========================================
echo 重启完成！
echo 访问地址:
echo   - 前端: http://localhost:3000/admin-users  
echo   - API: http://localhost:8000/api/v1/admin-users/
echo ========================================
pause