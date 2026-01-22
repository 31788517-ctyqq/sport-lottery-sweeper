@echo off
echo.
echo ========================================
echo   竞彩足球扫盘系统 - 项目启动脚本
echo ========================================
echo.
echo 时间: %DATE% %TIME%
echo.

REM 设置项目路径
set BACKEND_DIR=%~dp0
set FRONTEND_DIR=%BACKEND_DIR%frontend

echo 📍 后端路径: %BACKEND_DIR%
echo 📍 前端路径: %FRONTEND_DIR%
echo.

REM 检查Node.js
echo 🔍 检查环境...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js 未找到，请安装 Node.js 18 或更高版本
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('node --version') do set NODE_VERSION=%%i
    echo ✅ Node.js 版本: !NODE_VERSION!
)

REM 检查Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 未找到，请安装 Python 3.8 或更高版本
    pause
    exit /b 1
) else (
    echo ✅ Python 已找到
)

echo.
echo 🚀 启动后端服务...

REM 尝试终止可能占用端口的进程
echo 🔧 检查端口占用情况...
netstat -ano | findstr :8000 >nul
if %errorlevel% equ 0 (
    echo ⚠️  端口 8000 被占用，正在释放...
    for /f "tokens=5" %%i in ('netstat -ano ^| findstr :8000') do (
        if not "%%i"=="" (
            taskkill /f /pid %%i >nul 2>&1
            echo ✅ 已终止 PID %%i
        )
    )
)

netstat -ano | findstr :8001 >nul
if %errorlevel% equ 0 (
    echo ⚠️  端口 8001 被占用，正在释放...
    for /f "tokens=5" %%i in ('netstat -ano ^| findstr :8001') do (
        if not "%%i"=="" (
            taskkill /f /pid %%i >nul 2>&1
            echo ✅ 已终止 PID %%i
        )
    )
)

REM 启动后端服务
echo 🌐 启动后端服务 (端口 8001)...
start "Sport-Lottery-Backend" cmd /c "cd /d %BACKEND_DIR% && python -c \"from src.backend.optimized_main import app; import uvicorn; uvicorn.run(app, host='127.0.0.1', port=8001, log_level='info')\""

timeout /t 5 /nobreak >nul

REM 启动前端服务
echo 🖥️  启动前端服务 (端口 3000)...
if exist "%FRONTEND_DIR%" (
    echo 📦 检查前端依赖...
    cd /d %FRONTEND_DIR%
    
    REM 检查是否已安装依赖
    if not exist "node_modules" (
        echo 📦 安装前端依赖...
        npm install
    )
    
    echo 🚀 启动前端开发服务器...
    start "Sport-Lottery-Frontend" cmd /c "npm run dev"
) else (
    echo ⚠️  前端目录不存在: %FRONTEND_DIR%
)

echo.
echo ========================================
echo 🎯 访问地址:
echo   后端 API: http://127.0.0.1:8001
echo   后端文档: http://127.0.0.1:8001/docs
echo   前端界面: http://127.0.0.1:3000
echo   前端竞彩页面: http://127.0.0.1:3000/jczq
echo ========================================
echo.
echo 📝 注意事项:
echo   1. 确保防火墙允许相关端口通信
echo   2. 如前端无法连接后端，请检查代理配置
echo   3. 如果服务启动失败，请查看对应日志
echo.
pause