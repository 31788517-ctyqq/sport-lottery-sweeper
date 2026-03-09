@echo off
echo ========================================
echo 运行足球SP管理数据源页面端到端测试
echo ========================================

REM 检查是否在前端目录
if not exist "package.json" (
    echo 错误：请在frontend目录下运行此脚本
    pause
    exit /b 1
)

REM 检查Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Node.js，请先安装Node.js
    pause
    exit /b 1
)

REM 检查依赖
if not exist "node_modules" (
    echo 未找到node_modules，正在安装依赖...
    npm install
)

REM 检查Playwright浏览器
echo 检查Playwright浏览器安装...
npx playwright install chromium 2>nul

REM 启动前端服务器（如果未运行）
echo 启动前端开发服务器...
start /B npm run dev

REM 等待服务器启动
echo 等待服务器启动（5秒）...
timeout /t 5 /nobreak >nul

REM 运行测试
echo 开始运行端到端测试...
npx playwright test tests/e2e/data-source-management.spec.js --headed

REM 暂停查看结果
pause