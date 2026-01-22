@echo off
chcp 65001 >nul
echo ====================================
echo 前端启动脚本 (修复版)
echo ====================================
echo.

REM 切换到frontend目录
cd /d "%~dp0frontend"
echo 当前目录: %CD%
echo.

echo [1/4] 检查Node.js和pnpm...
where node >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Node.js未安装!
    pause
    exit /b 1
)

where pnpm >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pnpm未安装!
    echo 请先安装pnpm: npm install -g pnpm
    pause
    exit /b 1
)

node --version
pnpm --version
echo ✅ Node.js和pnpm已安装
echo.

echo [2/4] 检查package.json...
if not exist package.json (
    echo ❌ package.json不存在!
    echo 当前目录: %CD%
    dir package.json
    pause
    exit /b 1
)
echo ✅ package.json存在
echo.

echo [3/4] 检查依赖...
if not exist node_modules (
    echo ⚠️ node_modules不存在
    echo 正在安装依赖...
    pnpm install
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装失败!
        pause
        exit /b 1
    )
    echo ✅ 依赖安装成功
) else (
    echo ✅ node_modules已存在
)
echo.

echo [4/4] 启动前端开发服务器...
echo ====================================
echo 前端将在以下地址运行:
echo   - 本地: http://localhost:3000
echo   - 网络: http://0.0.0.0:3000
echo ====================================
echo.
echo 按 Ctrl+C 停止服务器
echo.

REM 使用绝对路径调用pnpm,避免路径问题
%LOCALAPPDATA%\pnpm\pnpm.exe run dev

pause
