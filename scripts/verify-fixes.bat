@echo off
chcp 65001 >nul
echo ====================================
echo 项目优化验证脚本
echo ====================================
echo.

set ERROR_COUNT=0

echo [1/6] 检查代码质量...
cd backend
python -m py_compile optimized_main.py 2>nul
if %errorlevel% neq 0 (
    echo ❌ optimized_main.py 语法错误
    set /a ERROR_COUNT+=1
) else (
    echo ✅ optimized_main.py 语法正确
)

python -m py_compile main.py 2>nul
if %errorlevel% neq 0 (
    echo ❌ main.py 语法错误
    set /a ERROR_COUNT+=1
) else (
    echo ✅ main.py 语法正确
)

python -m py_compile fast_startup_main.py 2>nul
if %errorlevel% neq 0 (
    echo ❌ fast_startup_main.py 语法错误
    set /a ERROR_COUNT+=1
) else (
    echo ✅ fast_startup_main.py 语法正确
)

python -m py_compile production_main.py 2>nul
if %errorlevel% neq 0 (
    echo ❌ production_main.py 语法错误
    set /a ERROR_COUNT+=1
) else (
    echo ✅ production_main.py 语法正确
)

echo.
echo [2/6] 检查调试文件...
if exist debug (
    echo ✅ debug 目录存在
) else (
    echo ❌ debug 目录不存在
    set /a ERROR_COUNT+=1
)

dir /b debug\debug_*.py 2>nul | findstr /r "." >nul
if %errorlevel% equ 0 (
    echo ✅ 调试文件已移动
) else (
    echo ⚠️  调试文件可能未完全移动
)

echo.
echo [3/6] 检查数据库文件...
if exist sport_lottery.db (
    echo ✅ sport_lottery.db 存在
) else (
    echo ❌ sport_lottery.db 不存在
    set /a ERROR_COUNT+=1
)

if exist sql_app.db (
    echo ❌ sql_app.db 仍然存在(应删除)
    set /a ERROR_COUNT+=1
) else (
    echo ✅ sql_app.db 已清理
)

echo.
echo [4/6] 检查前端依赖...
cd ..\frontend
if exist node_modules (
    echo ✅ node_modules 目录存在
    echo 📊 依赖包数量:
    dir /b node_modules 2>nul | find /c /v ""
) else (
    echo ❌ node_modules 不存在
    echo 📝 请运行: scripts\install-frontend-deps.bat
    set /a ERROR_COUNT+=1
)

echo.
echo [5/6] 检查工具脚本...
cd ..\scripts
if exist install-frontend-deps.bat (
    echo ✅ install-frontend-deps.bat 存在
) else (
    echo ❌ install-frontend-deps.bat 不存在
    set /a ERROR_COUNT+=1
)

if exist verify-fixes.bat (
    echo ✅ verify-fixes.bat 存在
) else (
    echo ⚠️  verify-fixes.bat 不存在
)

echo.
echo [6/6] 检查报告文档...
cd ..
if exist PROJECT_FIX_REPORT.md (
    echo ✅ PROJECT_FIX_REPORT.md 存在
) else (
    echo ❌ PROJECT_FIX_REPORT.md 不存在
    set /a ERROR_COUNT+=1
)

echo.
echo ====================================
if %ERROR_COUNT% equ 0 (
    echo ✅ 所有检查通过!
    echo 项目健康度: 优秀
) else (
    echo ⚠️  发现 %ERROR_COUNT% 个问题
    echo 项目健康度: 需要改进
)
echo ====================================
pause
