@echo off
REM 快速启动前端 - 一键启动脚本
REM 使用方法: 直接双击此文件

chcp 65001 >nul
cls

echo.
echo ====================================
echo   竞彩足球扫盘系统 - 快速启动
echo ====================================
echo.

REM 切换到frontend目录
cd /d "%~dp0frontend"

if not exist package.json (
    echo.
    echo ❌ 错误: package.json未找到!
    echo.
    echo 当前目录: %CD%
    echo.
    echo 请确保此文件位于项目根目录:
    echo c:\Users\11581\Downloads\sport-lottery-sweeper
    echo.
    pause
    exit /b 1
)

echo 正在启动前端服务器...
echo.
echo ====================================
echo 服务地址:
echo   http://localhost:3000
echo ====================================
echo.
echo 注意: 首次启动可能需要1-2分钟
echo       请等待 VITE 编译完成
echo.
echo 按 Ctrl+C 可停止服务
echo.

pnpm run dev

if %errorlevel% neq 0 (
    echo.
    echo ====================================
    echo 启动失败! 请检查:
    echo ====================================
    echo.
    echo 1. 是否已安装 pnpm?
    echo    如果没有,请运行: npm install -g pnpm
    echo.
    echo 2. node_modules是否存在?
    echo    如果不存在,请先安装依赖: pnpm install
    echo.
    echo 3. 端口3000是否被占用?
    echo    查看占用: netstat -ano ^| findstr :3000
    echo.
    pause
)
