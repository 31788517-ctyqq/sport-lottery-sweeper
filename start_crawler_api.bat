@echo off
chcp 65001 >nul
echo ========================================
echo 启动爬虫管理API服务
echo ========================================
echo.

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请安装Python 3.x
    pause
    exit /b 1
)

echo Python环境检查通过
python --version
echo.

:: 切换到项目目录
cd /d c:\Users\11581\Downloads\sport-lottery-sweeper
echo 当前目录: %CD%
echo.

:: 检查端口占用
netstat -ano | findstr :8000 >nul 2>&1
if %errorlevel% equ 0 (
    echo 警告: 端口8000已被占用
    echo 正在尝试终止占用进程...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
        taskkill /f /pid %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

echo.
echo 启动API服务...
echo 服务地址: http://localhost:8000
echo API文档:  http://localhost:8000/docs
echo 按 Ctrl+C 停止服务
echo ========================================
echo.

:: 启动服务
python backend_simple_main.py

if %errorlevel% neq 0 (
    echo.
    echo 服务启动失败，请检查错误信息
    pause
)

echo.
echo 服务已停止
echo ========================================