@echo off
echo ====================================
echo Phase 1 回滚脚本
echo ====================================
echo.

cd /d %~dp0..

echo [警告] 此操作将撤销 Phase 1 的所有改动！
echo.
echo 即将回滚：
echo - Backend 临时文件移动
echo - 前端目录结构调整
echo.
choice /c YN /m "确认回滚"

if errorlevel 2 (
    echo.
    echo 回滚已取消
    pause
    exit /b 0
)

echo.
echo 开始回滚...
echo.

:: 回滚 backend
echo [1/2] 回滚 Backend...
if exist ".naming-optimization\backend-files-before.txt" (
    :: 将文件移回原位置
    if exist "backend\debug\*.py" move /y "backend\debug\*.py" "backend\" >nul 2>&1
    if exist "backend\scripts\crawlers\*.py" move /y "backend\scripts\crawlers\*.py" "backend\" >nul 2>&1
    if exist "backend\tests\integration\*.py" move /y "backend\tests\integration\*.py" "backend\" >nul 2>&1
    if exist "backend\scripts\*.py" move /y "backend\scripts\*.py" "backend\" >nul 2>&1
    
    :: 删除空目录
    if exist "backend\debug" rmdir /s /q "backend\debug" 2>nul
    if exist "backend\scripts\crawlers" rmdir /s /q "backend\scripts\crawlers" 2>nul
    if exist "backend\scripts" rmdir /s /q "backend\scripts" 2>nul
    if exist "backend\tests\integration" rmdir /s /q "backend\tests\integration" 2>nul
    
    echo     ✓ Backend 回滚完成
) else (
    echo     ⚠️  未找到备份信息
)

:: 回滚 frontend
echo.
echo [2/2] 回滚 Frontend...
if exist ".naming-optimization\components-store-backup" (
    :: 恢复旧目录
    xcopy ".naming-optimization\components-store-backup" "frontend\src\components\store\" /E /I /Y >nul
    
    :: 删除新目录（可选）
    echo 是否删除新创建的 stores/modules 和 stores/plugins？
    choice /c YN /m "确认删除"
    if not errorlevel 2 (
        if exist "frontend\src\stores\modules" rmdir /s /q "frontend\src\stores\modules"
        if exist "frontend\src\stores\plugins" rmdir /s /q "frontend\src\stores\plugins"
    )
    
    echo     ✓ Frontend 回滚完成
) else (
    echo     ⚠️  未找到 Frontend 备份
)

echo.
echo ====================================
echo ✅ 回滚完成！
echo ====================================
echo.
echo 系统已恢复到 Phase 1 执行前的状态
echo.
echo 建议：
echo 1. 运行测试验证系统正常
echo 2. 删除 .naming-optimization 目录（如不再需要）
echo.
pause
