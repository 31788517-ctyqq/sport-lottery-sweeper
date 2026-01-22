@echo off
echo ====================================
echo Phase 1: 清理 Backend 临时文件
echo ====================================
echo.

cd /d %~dp0..

:: 检查是否在正确的目录
if not exist "backend" (
    echo [错误] 未找到 backend 目录！
    pause
    exit /b 1
)

:: 创建备份
echo [1/6] 创建备份...
if not exist ".naming-optimization" mkdir ".naming-optimization"
dir backend\*.py /b > .naming-optimization\backend-files-before.txt
echo     ✓ 备份文件列表已保存

:: 创建目标目录
echo.
echo [2/6] 创建目标目录...
if not exist "backend\debug" mkdir "backend\debug"
if not exist "backend\scripts" mkdir "backend\scripts"
if not exist "backend\scripts\crawlers" mkdir "backend\scripts\crawlers"
if not exist "backend\tests\integration" mkdir "backend\tests\integration"
echo     ✓ 目录结构已创建

:: 移动调试文件
echo.
echo [3/6] 移动调试文件...
for %%f in (backend\debug_*.py) do (
    if exist "%%f" (
        move "%%f" "backend\debug\" >nul
        echo     ✓ %%f
    )
)

:: 移动数据采集脚本
echo.
echo [4/6] 移动数据采集脚本...
for %%f in (backend\get_*.py backend\*_sporttery_*.py backend\*_crawler*.py) do (
    if exist "%%f" (
        move "%%f" "backend\scripts\crawlers\" >nul
        echo     ✓ %%f
    )
)

:: 移动测试文件
echo.
echo [5/6] 移动测试文件...
for %%f in (backend\verify_*.py backend\check_*.py) do (
    if exist "%%f" (
        move "%%f" "backend\tests\integration\" >nul
        echo     ✓ %%f
    )
)

:: 移动其他脚本
echo.
echo [6/6] 移动其他脚本...
for %%f in (backend\show_*.py backend\run_*.py backend\find_*.py backend\inspect_*.py backend\submit_*.py backend\use_*.py) do (
    if exist "%%f" (
        move "%%f" "backend\scripts\" >nul
        echo     ✓ %%f
    )
)

:: 移动特殊文件
if exist "backend\simple_server.py" move "backend\simple_server.py" "backend\scripts\" >nul
if exist "backend\fast_startup_main.py" move "backend\fast_startup_main.py" "backend\scripts\" >nul
if exist "backend\optimized_main.py" move "backend\optimized_main.py" "backend\scripts\" >nul
if exist "backend\production_main.py" move "backend\production_main.py" "backend\scripts\" >nul
if exist "backend\final_test.py" move "backend\final_test.py" "backend\tests\integration\" >nul

:: 统计结果
echo.
echo ====================================
echo 清理完成！
echo ====================================
dir backend\*.py /b > .naming-optimization\backend-files-after.txt
echo.
echo 清理前文件数: 
for /f %%a in ('type .naming-optimization\backend-files-before.txt ^| find /c /v ""') do echo     %%a 个
echo 清理后文件数:
for /f %%a in ('type .naming-optimization\backend-files-after.txt ^| find /c /v ""') do echo     %%a 个
echo.

:: 列出需要手动处理的重复文件
echo ⚠️  请手动检查以下重复文件：
echo.
if exist "backend\scripts\crawlers\*_optimized*.py" (
    echo [重复版本] *_optimized*.py
    dir backend\scripts\crawlers\*_optimized*.py /b
)
if exist "backend\scripts\crawlers\*_enhanced*.py" (
    echo [重复版本] *_enhanced*.py
    dir backend\scripts\crawlers\*_enhanced*.py /b
)
if exist "backend\scripts\crawlers\*_final*.py" (
    echo [重复版本] *_final*.py
    dir backend\scripts\crawlers\*_final*.py /b
)
echo.

echo ✅ Phase 1 完成！
echo.
echo 下一步：
echo 1. 检查上面列出的重复文件，手动删除旧版本
echo 2. 运行测试验证：pytest backend/tests/
echo 3. 如有问题，查看 .naming-optimization\ 目录中的备份
echo.
pause
