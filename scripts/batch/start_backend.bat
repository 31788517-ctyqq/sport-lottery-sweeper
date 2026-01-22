@echo off
cd /d %~dp0

echo ========================================
echo 1. 执行数据库结构迁移...
alembic upgrade head
if errorlevel 1 (
    echo ❌ 数据库迁移失败，终止启动
    pause
    exit /b 1
)

echo ========================================
echo 2. 执行种子数据导入...
python scripts/seed/seed_runner.py
if errorlevel 1 (
    echo ❌ 种子数据导入失败，终止启动
    pause
    exit /b 1
)

echo ========================================
echo 3. 执行数据库健康检查...
python scripts/health_check/db_health_check.py
if errorlevel 1 (
    echo ❌ 数据库健康检查未通过，终止启动
    pause
    exit /b 1
)

echo ========================================
echo 4. 启动后端服务...
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

pause
