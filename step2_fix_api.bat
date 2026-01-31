@echo off
cd /d c:\Users\11581\Downloads\sport-lottery-sweeper

echo ============================================
echo 🔧 第二步：修复后端API路由
echo ============================================
echo.

echo 1️⃣ 检查backend/main.py中的路由注册...
echo.

:: 检查lottery路由是否已注册
findstr "from backend.api.v1.lottery import router as lottery_router" backend\main.py >nul
if %errorlevel% equ 0 (
    echo ✓ lottery路由已存在
) else (
    echo ⚠ lottery路由不存在，需要添加
    echo.
    
    :: 备份原文件
    copy backend\main.py backend\main.py.backup
    echo ✓ 已备份 main.py 到 main.py.backup
    
    :: 添加lottery路由注册（在第66-70行后插入）
    (
        type backend\main.py | findstr /n /r "^" | findstr /v "竞彩足球数据路由"
        echo.
        echo :: 注册竞彩足球数据路由（前端需要的）
        echo try:
        echo     from backend.api.v1.lottery import router as lottery_router
        echo     app.include_router(lottery_router, prefix="/api/v1/lottery", tags=["lottery"])
        echo     logger.info("竞彩足球数据路由已成功注册")
        echo except Exception as e:
        echo     logger.error(f"竞彩足球数据路由注册失败: {e}")
    ) > temp_main.py
    
    move /y temp_main.py backend\main.py
    echo ✓ 已添加lottery路由注册
)

echo.
echo 2️⃣ 重启后端服务...
echo.

:: 停止现有Python进程（端口8000）
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
    echo ✓ 已停止占用8000端口的进程 (PID: %%a)
)

echo.
echo 3️⃣ 启动新的后端服务...
echo.

:: 启动后端服务
cd backend
start /B python main.py > backend.log 2>&1
timeout /t 3 /nobreak >nul

:: 检查服务是否启动
curl -s http://localhost:8000/health/live >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ 后端服务已启动 (端口: 8000)
) else (
    echo ⚠ 服务启动可能有问题，请检查 backend.log
)

echo.
echo 4️⃣ 验证API接口...
echo.

curl -s "http://localhost:8000/api/v1/lottery/matches?size=3" > api_test.json 2>&1

:: 检查API是否返回数据
findstr /c:"success" api_test.json >nul
if %errorlevel% equ 0 (
    echo ✓ API接口正常工作
    echo.
    type api_test.json
) else (
    echo ⚠ API可能有问题
    echo 请访问 http://localhost:8000/docs 查看API文档
    echo 或直接访问: http://localhost:8000/api/v1/lottery/matches?size=3
)

echo.
echo ============================================
echo ✅ 第二步完成！
echo ============================================
echo.
echo 下一步：执行第三步（验证前端显示）
echo.
pause
