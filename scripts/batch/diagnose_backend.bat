@echo off
cd /d %~dp0
echo 开始诊断后端...
echo.

python quick_start_backend.py > backend_startup.log 2>&1

echo.
echo 启动日志已保存到: backend_startup.log
echo 请查看该文件了解错误详情
pause
