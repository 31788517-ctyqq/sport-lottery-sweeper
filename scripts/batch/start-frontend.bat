@echo off
chcp 65001 >nul
echo ====================================
echo 前端启动脚本
echo ====================================
echo.

cd /d "%~dp0frontend"

echo [1/3] 检查环境...
node --version
npm --version

if not exist package.json (
    echo ❌ package.json 不存在!
    exit /b 1
)

echo ✅ package.json 存在
echo.

echo [2/3] 检查依赖...
if not exist node_modules (
    echo ⚠️ node_modules 不存在
    echo 正在安装依赖...
    pnpm install
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装失败!
        exit /b 1
    )
)
echo ✅ 依赖已安装
echo.

echo [3/3] 启动前端开发服务器...
echo.
echo ====================================
echo 前端将在以下地址运行:
echo   - 本地: http://localhost:3000
echo   - 网络: http://0.0.0.0:3000
echo ====================================
echo.
echo 按 Ctrl+C 停止服务器
echo.

pnpm run dev

pause
