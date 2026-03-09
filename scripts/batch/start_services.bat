@echo off
chcp 65001 >nul
echo ========================================
echo    竞彩扫盘系统 - 启动服务
echo ========================================
echo.

REM 停止所有旧进程
echo [1/4] 停止旧的服务进程...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 2 /nobreak >nul

REM 启动后端
echo.
echo [2/4] 启动后端服务 (端口 8000)...
start "后端服务" cmd /k "cd /d %~dp0 && uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 5 /nobreak >nul

REM 测试后端
echo.
echo [3/4] 测试后端健康状态...
powershell -Command "try { $r = Invoke-RestMethod -Uri 'http://localhost:8000/health' -TimeoutSec 5; Write-Host '✓ 后端启动成功' -ForegroundColor Green } catch { Write-Host '✗ 后端启动失败' -ForegroundColor Red }"

REM 启动前端
echo.
echo [4/4] 启动前端服务 (端口 3000)...
start "前端服务" cmd /k "cd /d %~dp0\frontend && npm run dev"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo    服务启动完成!
echo ========================================
echo.
echo 后端地址: http://localhost:8000
echo 后端文档: http://localhost:8000/docs
echo 前端地址: http://localhost:3000
echo 管理登录: http://localhost:3000/#/admin/login
echo.
echo 测试账号:
echo   用户名: admin
echo   密码:   admin123
echo.
echo 按任意键打开浏览器...
pause >nul
start http://localhost:3000/#/admin/login
