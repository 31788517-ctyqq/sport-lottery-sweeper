@echo off
chcp 65001 > nul
cd /d %~dp0

echo ╔════════════════════════════════════════════════════════════╗
echo ║     🔍 前端问题诊断工具                                    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo 📋 检查项目配置...
echo ════════════════════════════════════════════════════════════
echo.

:: 检查Node.js
echo [1/6] 检查 Node.js
node --version > nul 2>&1
if errorlevel 1 (
    echo    ❌ Node.js 未安装
) else (
    node --version | findstr /C:"v"
    echo    ✅ Node.js 已安装
)
echo.

:: 检查npm
echo [2/6] 检查 npm
npm --version > nul 2>&1
if errorlevel 1 (
    echo    ❌ npm 未安装
) else (
    npm --version
    echo    ✅ npm 已安装
)
echo.

:: 检查frontend目录
echo [3/6] 检查 frontend 目录
if exist "frontend" (
    echo    ✅ frontend 目录存在
) else (
    echo    ❌ frontend 目录不存在
)
echo.

:: 检查关键文件
echo [4/6] 检查关键文件
if exist "frontend\src\App.vue" (
    echo    ✅ App.vue 存在
) else (
    echo    ❌ App.vue 不存在
)

if exist "frontend\src\main.js" (
    echo    ✅ main.js 存在
) else (
    echo    ❌ main.js 不存在
)

if exist "frontend\src\router\index.js" (
    echo    ✅ router/index.js 存在
) else (
    echo    ❌ router/index.js 不存在
)

if exist "frontend\src\views\JczqSchedule.vue" (
    echo    ✅ JczqSchedule.vue 存在
) else (
    echo    ❌ JczqSchedule.vue 不存在
)
echo.

:: 检查依赖
echo [5/6] 检查 node_modules
if exist "frontend\node_modules" (
    echo    ✅ node_modules 已安装
) else (
    echo    ⚠️  node_modules 未安装，需要运行 npm install
)
echo.

:: 检查端口
echo [6/6] 检查端口 5173
netstat -ano | findstr :5173 > nul
if errorlevel 1 (
    echo    ✅ 端口 5173 未被占用
) else (
    echo    ⚠️  端口 5173 已被占用
    echo    占用端口的进程:
    netstat -ano | findstr :5173
)
echo.

echo ════════════════════════════════════════════════════════════
echo 📊 诊断结果
echo ════════════════════════════════════════════════════════════
echo.

if exist "frontend\src\router\index.js" (
    echo 🔍 检查路由配置...
    findstr /C:"jczq-schedule" frontend\src\router\index.js > nul
    if errorlevel 1 (
        echo    ⚠️  路由中未找到 jczq-schedule 配置
    ) else (
        echo    ✅ 路由已配置 jczq-schedule
    )
)
echo.

if exist "frontend\src\main.js" (
    echo 🔍 检查 main.js 路由导入...
    findstr /C:"router" frontend\src\main.js > nul
    if errorlevel 1 (
        echo    ⚠️  main.js 中未导入路由
    ) else (
        echo    ✅ main.js 已导入路由
    )
)
echo.

if exist "frontend\src\App.vue" (
    echo 🔍 检查 App.vue router-view...
    findstr /C:"router-view" frontend\src\App.vue > nul
    if errorlevel 1 (
        echo    ⚠️  App.vue 中未使用 router-view
    ) else (
        echo    ✅ App.vue 已使用 router-view
    )
)
echo.

echo ════════════════════════════════════════════════════════════
echo 💡 建议操作
echo ════════════════════════════════════════════════════════════
echo.

if not exist "frontend\node_modules" (
    echo 1. 安装依赖: cd frontend ^&^& npm install
)

netstat -ano | findstr :5173 > nul
if not errorlevel 1 (
    echo 2. 停止占用端口的进程
)

echo 3. 重启前端: restart_frontend.bat
echo 4. 访问页面: http://localhost:5173/#/jczq-schedule
echo.

echo ════════════════════════════════════════════════════════════
echo.
pause
