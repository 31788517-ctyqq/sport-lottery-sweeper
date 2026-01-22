@echo off
echo ========================================
echo 前端文件完整性检查
echo ========================================
echo.

echo [1/6] 检查 index.html...
if exist "frontend\public\index.html" (
    echo [OK] index.html 存在
) else (
    echo [ERROR] index.html 不存在!
    pause
    exit /b 1
)

echo.
echo [2/6] 检查 main.js...
if exist "frontend\src\main.js" (
    echo [OK] main.js 存在
) else (
    echo [ERROR] main.js 不存在!
    pause
    exit /b 1
)

echo.
echo [3/6] 检查 App.vue...
if exist "frontend\src\App.vue" (
    echo [OK] App.vue 存在
) else (
    echo [ERROR] App.vue 不存在!
    pause
    exit /b 1
)

echo.
echo [4/6] 检查 stores/app.js...
if exist "frontend\src\stores\app.js" (
    echo [OK] stores/app.js 存在
) else (
    echo [ERROR] stores/app.js 不存在!
    pause
    exit /b 1
)

echo.
echo [5/6] 检查 main-content.css...
if exist "frontend\src\styles\main-content.css" (
    echo [OK] main-content.css 存在
) else (
    echo [ERROR] main-content.css 不存在!
    pause
    exit /b 1
)

echo.
echo [6/6] 检查依赖是否安装...
if exist "frontend\node_modules" (
    echo [OK] node_modules 存在
) else (
    echo [WARNING] node_modules 不存在,需要安装依赖
    echo 请运行: pnpm install
)

echo.
echo ========================================
echo 所有核心文件检查完成!
echo ========================================
echo.
echo 现在请执行以下步骤:
echo 1. 确保 Vite 服务器正在运行
echo 2. 访问 http://localhost:3000
echo 3. 如果页面空白,按 Ctrl+F5 硬刷新
echo 4. 检查浏览器控制台(F12)的错误
echo.
pause
