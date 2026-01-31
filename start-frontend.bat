@echo off
title 体育彩票扫盘系统前端启动脚本

echo.
echo ================================
echo   体育彩票扫盘系统前端启动脚本
echo ================================
echo.

REM 切换到frontend目录
cd /d "%~dp0frontend"

REM 检查是否安装了npm
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到npm，请先安装Node.js
    pause
    exit /b 1
)

REM 检查是否安装了依赖
if not exist "node_modules" (
    echo 检测到未安装依赖，开始安装...
    npm install
    if %errorlevel% neq 0 (
        echo 依赖安装失败，请检查网络连接或npm配置
        pause
        exit /b 1
    )
    echo 依赖安装完成
    echo.
)

REM 尝试启动前端开发服务器，如果3004端口被占用，则依次尝试3005, 3006, 3007
set PORT=3004
:check_port
netstat -an | find ":%PORT%" >nul
if %errorlevel% equ 0 (
    echo 端口 %PORT% 已被占用
    if %PORT% geq 3007 (
        echo 所有预设端口都被占用，请手动释放端口后重试
        pause
        exit /b 1
    )
    set /a PORT+=1
    echo 尝试端口 %PORT%
    goto check_port
)

echo 正在启动前端开发服务器，端口: %PORT%
npm run dev -- --port %PORT%

pause