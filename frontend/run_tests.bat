@echo off
chcp 65001 >nul
echo ========================================
echo  BeidanFilterPanel 测试运行器
echo ========================================
echo.

cd /d %~dp0frontend

echo 检查文件结构...
if not exist "tests\unit\views\admin\BeidanFilterPanel.unit.spec.js" (
    echo ❌ 测试文件不存在
    pause
    exit /b 1
)

echo ✅ 测试文件找到

if not exist "src\views\admin\BeidanFilterPanel.vue" (
    echo ❌ 组件文件不存在
    pause
    exit /b 1
)

echo ✅ 组件文件找到
echo.

echo 运行单元测试...
echo ========================================

:: 使用 npx vitest 运行测试，设置超时防止挂起
npx vitest run tests/unit/views/admin/BeidanFilterPanel.unit.spec.js --reporter=verbose --timeout=30000

if errorlevel 1 (
    echo.
    echo ❌ 测试执行失败
) else (
    echo.
    echo ✅ 测试执行完成
)

echo.
pause