@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ========================================
echo 🧹 体育彩票扫盘系统 - 备份文件清理工具
echo ========================================
echo.

:: 设置项目根目录
cd /d "%~dp0.."

:: 默认参数
set RETENTION_DAYS=30
set DRY_RUN=false
set VERBOSE=false

:: 解析命令行参数
:parse_args
if "%1"=="" goto end_parse
if "%1"=="--days" (
    set RETENTION_DAYS=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--dry-run" (
    set DRY_RUN=true
    shift
    goto parse_args
)
if "%1"=="--verbose" (
    set VERBOSE=true
    shift
    goto parse_args
)
if "%1"=="--help" (
    goto show_help
)

shift
goto parse_args

:show_help
echo 用法: cleanup_backups.bat [选项]
echo.
echo 选项:
echo   --days N         保留天数 (默认: 30)
echo   --dry-run        试运行模式，不实际删除文件
echo   --verbose        显示详细信息
echo   --help           显示此帮助信息
echo.
echo 示例:
echo   cleanup_backups.bat --days 15
echo   cleanup_backups.bat --dry-run --verbose
echo   cleanup_backups.bat --days 7
echo.
goto end

:end_parse

echo 📅 保留期限: !RETENTION_DAYS! 天
echo 🧪 试运行模式: !DRY_RUN!
echo.

:: 检查Python是否可用
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python，请确保Python已安装并添加到PATH
    pause
    exit /b 1
)

:: 检查清理脚本是否存在
if not exist "scripts\cleanup_old_backups.py" (
    echo ❌ 错误: 未找到清理脚本 scripts\cleanup_old_backups.py
    pause
    exit /b 1
)

:: 构建Python命令
set PYTHON_CMD=python scripts\cleanup_old_backups.py --days !RETENTION_DAYS!

if "!DRY_RUN!"=="true" (
    set PYTHON_CMD=!PYTHON_CMD! --dry-run
)

if "!VERBOSE!"=="true" (
    set PYTHON_CMD=!PYTHON_CMD! --verbose
)

:: 执行清理
echo 🚀 开始执行清理...
echo 命令: !PYTHON_CMD!
echo.
!PYTHON_CMD!

if errorlevel 1 (
    echo.
    echo ❌ 清理过程出现错误
    pause
    exit /b 1
)

echo.
echo ✅ 清理任务完成
echo.

:: 显示磁盘使用情况
echo 📊 当前磁盘使用情况:
dir "data" 2>nul | find "可用字节"

:end
pause