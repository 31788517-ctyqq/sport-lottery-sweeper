@echo off
echo Stopping Vite server on port 3000...

REM 查找并终止3000端口的进程
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
    echo Killing process PID: %%a
    taskkill /PID %%a /F
)

timeout /t 2 /nobreak > nul

echo Starting Vite server...
cd frontend
start "Vite Server" cmd /c "npm run dev"
cd ..

echo Vite server restart initiated. Check vite.out for logs.