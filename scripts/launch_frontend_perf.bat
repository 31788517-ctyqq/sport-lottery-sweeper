@echo off
setlocal enabledelayedexpansion

echo 🚀 启动前端性能监测脚本
echo ================================
echo 时间: %DATE% %TIME%
echo ================================

REM 记录开始时间
for /f "tokens=1-4 delims=:. " %%a in ("%time%") do (
    set /a "start_secs=%%a*3600+%%b*60+%%c"
    set /a "start_ms=%%d"
)

REM 检查Node.js版本
echo.
echo 检查环境...
node --version
if errorlevel 1 (
    echo ❌ Node.js 未安装或不在 PATH 中
    echo 请安装 Node.js 18.0.0 或更高版本
    pause
    exit /b 1
) else (
    for /f "tokens=2" %%i in ('node --version') do set NODE_VERSION=%%i
    echo ✅ Node.js 版本: !NODE_VERSION!
)

REM 检查包管理器
echo.
set PACKAGE_MANAGER=npm
where pnpm >nul 2>nul
if %errorlevel% == 0 (
    set PACKAGE_MANAGER=pnpm
    echo ✅ 包管理器: !PACKAGE_MANAGER!
) else (
    where yarn >nul 2>nul
    if %errorlevel% == 0 (
        set PACKAGE_MANAGER=yarn
        echo ✅ 包管理器: !PACKAGE_MANAGER!
    ) else (
        echo ✅ 包管理器: !PACKAGE_MANAGER! (pnpm/yarn 未安装，使用 npm)
    )
)

echo.
echo 🔍 启动时间监测:
pushd "..\frontend"

REM 记录启动开发服务器的时间
for /f "tokens=1-4 delims=:. " %%a in ("%time%") do (
    set /a "dev_start_secs=%%a*3600+%%b*60+%%c"
    set /a "dev_start_ms=%%d"
)

echo 启动前端开发服务器...
call !PACKAGE_MANAGER! run dev

REM 计算开发服务器启动时间
for /f "tokens=1-4 delims=:. " %%a in ("%time%") do (
    set /a "dev_end_secs=%%a*3600+%%b*60+%%c"
    set /a "dev_end_ms=%%d"
)

set /a "dev_duration_secs=!dev_end_secs!-!dev_start_secs!"
set /a "dev_duration_ms=!dev_end_ms!-!dev_start_ms!"
set /a "dev_total_ms=!dev_duration_secs!*100+!dev_duration_ms!"

echo ⚡ 开发服务器启动时间: !dev_total_ms! 毫秒

popd

REM 计算总时间
for /f "tokens=1-4 delims=:. " %%a in ("%time%") do (
    set /a "end_secs=%%a*3600+%%b*60+%%c"
    set /a "end_ms=%%d"
)

set /a "duration_secs=!end_secs!-!start_secs!"
set /a "duration_ms=!end_ms!-!start_ms!"
set /a "total_ms=!duration_secs!*100+!duration_ms!"

echo.
echo ================================
echo 🏁 任务完成
echo 总耗时: !total_ms! 毫秒
echo ================================

pause