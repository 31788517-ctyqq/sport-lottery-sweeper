@echo off
echo ========================================
echo 爬虫管理模块数据库迁移脚本
echo ========================================

:: 确保在项目根目录
cd /d %~dp0

:: 检查 alembic 命令是否可用
where alembic >nul 2>nul
if %errorlevel% neq 0 (
    echo 错误：未找到 alembic 命令，请先激活虚拟环境或安装 alembic
    pause
    exit /b 1
)

echo 1. 生成迁移脚本...
alembic revision --autogenerate -m "create crawler tables"
if %errorlevel% neq 0 (
    echo 生成迁移脚本失败
    pause
    exit /b 1
)

echo 2. 应用迁移（创建表）...
alembic upgrade head
if %errorlevel% neq 0 (
    echo 应用迁移失败
    pause
    exit /b 1
)

echo ========================================
echo 数据库迁移完成！爬虫管理表已创建。
echo ========================================
pause