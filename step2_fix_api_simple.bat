@echo off
cd /d c:\Users\11581\Downloads\sport-lottery-sweeper

echo ============================================
echo Step 2: Fix Backend API
echo ============================================
echo.

echo Checking lottery route...
findstr "from backend.api.v1.lottery import router as lottery_router" backend\main.py >nul
if %errorlevel% equ 0 (
    echo OK: lottery route exists
) else (
    echo WARNING: lottery route not found, adding...
    copy backend\main.py backend\main.py.backup
    echo OK: backup created
    
    echo.>> backend\main.py
    echo # Register lottery route>> backend\main.py
    echo try:>> backend\main.py
    echo     from backend.api.v1.lottery import router as lottery_router>> backend\main.py
    echo     app.include_router(lottery_router, prefix="/api/v1/lottery", tags=["lottery"])>> backend\main.py
    echo     logger.info("lottery route registered")>> backend\main.py
    echo except Exception as e:>> backend\main.py
    echo     logger.error(f"lottery route failed: {e}")>> backend\main.py
    echo OK: route added
)

echo.
echo Stopping service on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    taskkill /PID %%a /F >nul 2>&1
    echo Stopped PID %%a
)

echo.
echo Starting backend service...
cd backend
start /B python main.py > backend.log 2>&1
timeout /t 5 /nobreak >nul

curl -s http://localhost:8000/health/live >nul 2>&1
if %errorlevel% equ 0 (
    echo OK: service started
) else (
    echo WARNING: service may have issues
)

echo.
echo Testing API...
curl -s "http://localhost:8000/api/v1/lottery/matches?size=3" > api_test.json 2>&1
findstr "success" api_test.json >nul
if %errorlevel% equ 0 (
    echo OK: API is working
    type api_test.json
) else (
    echo WARNING: API may have issues
    echo Check: http://localhost:8000/api/v1/lottery/matches?size=3
)

echo.
echo ============================================
echo Step 2 Complete!
echo ============================================
echo.
pause
