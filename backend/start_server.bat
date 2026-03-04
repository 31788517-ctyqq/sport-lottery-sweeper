@echo off
chcp 65001 >nul
echo ========================================
echo      体育彩票扫盘系统 - 后端服务启动
echo ========================================
echo 端口固定: 8000
echo 地址: http://localhost:8000
echo.
echo 正在启动后端服务...
python start_server.py
pause