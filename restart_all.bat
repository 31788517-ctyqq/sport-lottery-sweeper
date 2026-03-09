@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ========================================
echo     一键重启前后端服务脚本
echo ========================================

:: 函数：杀死指定端口的进程
:kill_port
    set port=%1
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :%port% ^| findstr LISTENING') do (
        echo 正在终止占用端口 %port% 的进程 PID=%%a ...
        taskkill /PID %%a /F >nul 2>&1
    )
    exit /b

:: 停止现有服务
echo 停止现有的前后端服务...
call :kill_port 8001
call :kill_port 3000

echo 等待3秒...
timeout /t 3 /nobreak >nul

:: 启动后端服务
:start_backend
echo 启动后端服务...
cd /d "%~dp0"
if exist "%~dp0\backend\main.py" (
    start "Backend" /min python -m uvicorn backend.main:app --host localhost --port 8001
    echo 后端启动中... 请稍候。
) else (
    echo 错误: 未找到后端文件 backend\main.py！
    pause
    exit /b
)

:: 等待后端启动
echo 等待5秒让后端启动...
timeout /t 5 /nobreak >nul

:: 启动前端服务
:start_frontend
echo 启动前端服务...
cd /d "%~dp0\frontend"
if exist "%~dp0\frontend\package.json" (
    start "Frontend" /min cmd /c "npm run dev & pause"
    echo 前端启动中... 检查浏览器以获取确切地址。
) else (
    echo 警告: 未找到前端配置 frontend\package.json，跳过前端启动。
)

:: 完成提示
echo.
echo ========================================
echo       所有服务已尝试启动!
echo ========================================
echo 前端地址: http://localhost:3000 (或控制台显示的端口)
echo 后端地址: http://localhost:8001
echo.
echo 管理后台登录凭据:
echo   用户名: admin
echo   密码: admin123
echo.
echo 提示: 关闭此窗口将结束后台运行的服务。
echo ========================================
pause