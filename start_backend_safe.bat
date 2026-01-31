@echo off
chcp 65001 >nul
echo ========================================
echo 体育彩票扫盘系统 - 后端安全启动
echo ========================================
echo.

:: 检查端口8000是否被占用
netstat -ano | findstr :8000 > temp_port_check.txt 2>nul
set PORT_IN_USE=0
for /f "tokens=5" %%a in ('type temp_port_check.txt') do (
    set PORT_IN_USE=1
    echo 发现进程PID: %%a 占用端口8000
)
del temp_port_check.txt 2>nul

if %PORT_IN_USE%==1 (
    echo.
    echo ⚠️  端口8000被占用，正在清理...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
        taskkill /F /PID %%a >nul 2>&1
        echo 已终止进程 PID: %%a
    )
    timeout /t 2 /nobreak >nul
)

echo.
echo 🚀 启动后端服务 (端口8000)...
echo 工作目录: %cd%
echo 时间: %date% %time%
echo.

:: 设置环境变量确保UTF-8编码
set PYTHONIOENCODING=utf-8

:: 启动后端服务
python main.py

if errorlevel 1 (
    echo.
    echo ❌ 后端启动失败！
    echo 按任意键查看错误信息...
    pause >nul
) else (
    echo.
    echo ✅ 后端服务已停止
)