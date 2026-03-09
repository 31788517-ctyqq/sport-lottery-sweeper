@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

echo ========================================
echo 🕒 设置备份文件清理定时任务
echo ========================================
echo.

:: 检查是否以管理员权限运行
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ❌ 错误: 此脚本需要管理员权限运行
    echo    请右键点击此文件，选择"以管理员身份运行"
    pause
    exit /b 1
)

echo ✅ 已获得管理员权限
echo.

:: 设置项目路径
cd /d "%~dp0.."
set PROJECT_PATH=%CD%
set PYTHON_PATH=python
set SCRIPT_PATH=%PROJECT_PATH%\scripts\cleanup_old_backups.py

echo 📂 项目路径: !PROJECT_PATH!
echo 🐍 Python路径: !PYTHON_PATH!
echo 📜 脚本路径: !SCRIPT_PATH!
echo.

:: 创建每周执行的计划任务（每周日凌晨2点执行）
echo 📅 创建每周清理任务...

schtasks /create /tn "SportLottery-BackupCleanup-Weekly" /tr "!PYTHON_PATH! !SCRIPT_PATH! --days 30" /sc weekly /d SUN /st 02:00 /f /ru SYSTEM

if errorlevel 1 (
    echo ❌ 创建每周任务失败
) else (
    echo ✅ 每周清理任务已创建 (每周日凌晨2点)
)

echo.

:: 创建每月执行的深度清理任务（每月1号凌晨3点执行）
echo 📅 创建每月深度清理任务...

schtasks /create /tn "SportLottery-BackupCleanup-Monthly" /tr "!PYTHON_PATH! !SCRIPT_PATH! --days 90" /sc monthly /mo 1 /st 03:00 /f /ru SYSTEM

if errorlevel 1 (
    echo ❌ 创建每月任务失败
) else (
    echo ✅ 每月深度清理任务已创建 (每月1号凌晨3点)
)

echo.

:: 创建临时文件每日清理任务（每天凌晨1点执行）
echo 📅 创建每日临时文件清理任务...

schtasks /create /tn "SportLottery-TempCleanup-Daily" /tr "!PYTHON_PATH! !SCRIPT_PATH! --days 7" /sc daily /st 01:00 /f /ru SYSTEM

if errorlevel 1 (
    echo ❌ 创建每日任务失败
) else (
    echo ✅ 每日临时文件清理任务已创建 (每天凌晨1点)
)

echo.
echo ========================================
echo 📋 当前计划的清理任务:
echo ========================================
schtasks /query /fo table /tn "SportLottery-*"

echo.
echo ========================================
echo ✅ 定时任务设置完成！
echo ========================================
echo.
echo 📝 任务说明:
echo   • 每周清理: 删除30天前的备份文件
echo   • 每月清理: 删除90天前的旧备份文件 (深度清理)
echo   • 每日清理: 删除7天前的临时文件
echo.
echo 🔧 管理命令:
echo   • 查看任务: schtasks /query /tn "SportLottery-*"
echo   • 删除任务: schtasks /delete /tn "任务名称" /f
echo   • 手动执行: python scripts\cleanup_old_backups.py --days 30
echo.
echo 📊 监控日志: logs\backup_cleanup.log
echo.
pause