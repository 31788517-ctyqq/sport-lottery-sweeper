@echo off
chcp 65001 >nul
echo ========================================
echo 释放端口 8000
========================================
echo.

:: 查找并杀死占用8000端口的进程
echo 正在查找占用端口8000的进程...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    echo 发现进程 PID: %%a 占用端口8000
    taskkill /F /PID %%a
    echo 已终止进程 PID: %%a
)

echo.
echo ✅ 端口8000释放完成
echo 现在可以启动后端服务了
echo.
pause