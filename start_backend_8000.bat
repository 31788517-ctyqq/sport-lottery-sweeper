@echo off
echo 正在检查端口 8000 占用情况...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo 发现占用进程 PID: %%a
    taskkill /PID %%a /F
)
echo 端口释放完成，启动后端服务...
cd /d %~dp0backend
python main.py
pause