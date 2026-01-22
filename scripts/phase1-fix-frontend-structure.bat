@echo off
echo ====================================
echo Phase 1: 修复前端目录结构
echo ====================================
echo.

cd /d %~dp0..

:: 检查目录是否存在
if not exist "frontend\src\components\store" (
    echo [信息] components\store 目录不存在，无需处理
    echo ✅ 前端目录结构正常
    pause
    exit /b 0
)

echo [警告] 发现重复目录：frontend\src\components\store
echo.

:: 创建目标目录
echo [1/4] 创建目标目录...
if not exist "frontend\src\stores\modules" mkdir "frontend\src\stores\modules"
if not exist "frontend\src\stores\plugins" mkdir "frontend\src\stores\plugins"
echo     ✓ 目录已创建

:: 备份
echo.
echo [2/4] 备份现有文件...
if not exist ".naming-optimization" mkdir ".naming-optimization"
xcopy "frontend\src\components\store" ".naming-optimization\components-store-backup\" /E /I /Y >nul
echo     ✓ 备份到 .naming-optimization\components-store-backup\

:: 复制文件
echo.
echo [3/4] 移动文件...
if exist "frontend\src\components\store\modules\*.*" (
    xcopy "frontend\src\components\store\modules\*.*" "frontend\src\stores\modules\" /Y >nul
    echo     ✓ modules 已移动
)
if exist "frontend\src\components\store\plugins\*.*" (
    xcopy "frontend\src\components\store\plugins\*.*" "frontend\src\stores\plugins\" /Y >nul
    echo     ✓ plugins 已移动
)

:: 验证文件完整性
echo.
echo [4/4] 验证文件完整性...
set /a files_error=0
if not exist "frontend\src\stores\modules\*.*" set /a files_error=1
if not exist "frontend\src\stores\plugins\*.*" set /a files_error=1

if %files_error%==1 (
    echo     ❌ 文件移动失败！
    echo     保留原目录，请手动检查
    pause
    exit /b 1
)

echo     ✓ 文件完整性验证通过

:: 删除旧目录
echo.
echo 是否删除旧目录 frontend\src\components\store？
echo 文件已安全备份到 .naming-optimization\components-store-backup\
choice /c YN /m "确认删除"

if errorlevel 2 (
    echo.
    echo [跳过] 保留旧目录，请手动清理
) else (
    echo.
    echo 删除旧目录...
    rmdir /s /q "frontend\src\components\store"
    echo     ✓ 旧目录已删除
)

echo.
echo ====================================
echo ✅ Phase 1 前端目录修复完成！
echo ====================================
echo.
echo 新目录结构：
echo frontend\src\stores\
echo     ├── index.js
echo     ├── app.js
echo     ├── admin.js
echo     ├── modules\
echo     └── plugins\
echo.
echo 下一步：
echo 1. 更新导入路径（如有引用 components/store 的地方）
echo 2. 运行前端测试：npm run test
echo 3. 启动开发服务器：npm run dev
echo.
pause
