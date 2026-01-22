@echo off
chcp 65001 >nul
echo ====================================
echo 前端依赖安装脚本
echo ====================================
echo.

echo [1/3] 检查 Node.js 和 npm...
node --version
npm --version
echo.

echo [2/3] 进入前端目录并安装依赖...
cd /d "%~dp0frontend"
if not exist package.json (
    echo ❌ package.json 不存在!
    exit /b 1
)

echo 正在安装依赖...
echo 这可能需要几分钟时间,请耐心等待...
echo.

npm install --legacy-peer-deps

if %errorlevel% neq 0 (
    echo.
    echo ❌ 标准安装失败,尝试使用 --force 选项...
    npm install --force
    if %errorlevel% neq 0 (
        echo.
        echo ❌ 依赖安装失败!
        echo.
        echo 请检查:
        echo 1. 网络连接是否正常
        echo 2. npm 配置是否正确
        echo 3. package.json 是否有效
        exit /b 1
    )
)

echo.
echo [3/3] 验证依赖安装...
if exist node_modules (
    echo ✅ 依赖安装成功!
    echo.
    echo 📊 依赖统计:
    dir /b node_modules 2>nul | find /c /v ""
) else (
    echo ❌ node_modules 目录不存在!
    exit /b 1
)

echo.
echo ====================================
echo ✅ 安装完成!
echo.
echo 启动前端:
echo   cd frontend
echo   npm run dev
echo ====================================
pause
