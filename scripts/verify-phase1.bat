@echo off
echo ====================================
echo Phase 1 验证脚本
echo ====================================
echo.

cd /d %~dp0..

set /a errors=0

:: 检查 backend 清理
echo [1/5] 检查 Backend 清理结果...
if exist "backend\debug\debug_*.py" (
    echo     ✓ 调试文件已移动
) else (
    echo     ⚠️  未找到已移动的调试文件
    set /a errors+=1
)

if exist "backend\scripts\crawlers\get_*.py" (
    echo     ✓ 爬虫脚本已移动
) else (
    echo     ⚠️  未找到已移动的爬虫脚本
    set /a errors+=1
)

:: 检查 backend 核心文件
echo.
echo [2/5] 检查 Backend 核心文件...
set core_files=main.py config.py database.py models.py processor.py
for %%f in (%core_files%) do (
    if exist "backend\%%f" (
        echo     ✓ %%f 存在
    ) else (
        echo     ❌ %%f 缺失
        set /a errors+=1
    )
)

:: 检查前端目录结构
echo.
echo [3/5] 检查前端目录结构...
if exist "frontend\src\stores\index.js" (
    echo     ✓ stores 目录正常
) else (
    echo     ❌ stores 目录异常
    set /a errors+=1
)

if exist "frontend\src\components\store" (
    echo     ⚠️  旧目录 components\store 仍然存在
    echo        建议删除
) else (
    echo     ✓ 旧目录已清理
)

:: 检查导入路径
echo.
echo [4/5] 检查潜在的导入路径问题...
findstr /s /i "from backend.debug_" backend\*.py >nul 2>&1
if %errorlevel%==0 (
    echo     ⚠️  发现需要更新的导入路径
    echo        运行: findstr /s /i "from backend.debug_" backend\*.py
    set /a errors+=1
) else (
    echo     ✓ 未发现明显的导入路径问题
)

:: 检查文件权限和可读性
echo.
echo [5/5] 检查文件可访问性...
python --version >nul 2>&1
if %errorlevel%==0 (
    python -c "import backend.main" 2>nul
    if %errorlevel%==0 (
        echo     ✓ Backend 模块可导入
    ) else (
        echo     ⚠️  Backend 模块导入有问题
        echo        建议运行: python backend/main.py
        set /a errors+=1
    )
) else (
    echo     ⚠️  未找到 Python，跳过导入检查
)

:: 总结
echo.
echo ====================================
if %errors%==0 (
    echo ✅ 验证通过！所有检查项正常
    echo.
    echo 建议执行以下测试：
    echo 1. pytest backend/tests/ -v
    echo 2. python backend/main.py
    echo 3. npm run dev
) else (
    echo ⚠️  发现 %errors% 个问题
    echo.
    echo 请检查上述警告和错误信息
    echo 如需回滚，查看 .naming-optimization\ 目录
)
echo ====================================
echo.

pause
