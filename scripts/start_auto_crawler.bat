@echo off
chcp 65001 >nul
echo 🚀 启动500彩票网自动爬虫系统...

:: 检查Redis是否运行
echo 📋 检查Redis连接...
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo ❌ Redis未运行，请先启动Redis
    echo    可以使用: redis-server
    pause
    exit /b 1
)
echo ✅ Redis连接正常

:: 启动Celery Worker
echo 👷 启动Celery Worker...
start "Celery Worker" cmd /k "celery -A backend.tasks.celery_schedule worker --loglevel=info --queues=crawler,monitor"
echo    Worker已启动...

:: 等待Worker启动
timeout /t 3 /nobreak >nul

:: 启动Celery Beat (定时任务调度器)
echo ⏰ 启动Celery Beat...
start "Celery Beat" cmd /k "celery -A backend.tasks.celery_schedule beat --loglevel=info"
echo    Beat已启动...

:: 等待Beat启动
timeout /t 3 /nobreak >nul

echo ⏳ 等待服务启动...
timeout /t 5 /nobreak >nul

:: 测试立即执行一次抓取
echo 🧪 测试执行一次抓取...
celery -A backend.tasks.celery_schedule call tasks.500wang.fetch_daily_matches

echo.
echo ✅ 自动爬虫系统启动完成！
echo.
echo 📊 定时任务计划:
echo    - 每日08:00: 抓取3天赛程
echo    - 每小时整点: 更新最新数据
echo    - 每30分钟: 健康检查
echo.
echo 🔧 管理命令:
echo    - 查看任务: celery -A backend.tasks.celery_schedule inspect active
echo    - 手动执行: celery -A backend.tasks.celery_schedule call tasks.500wang.fetch_daily_matches
echo    - 停止系统: 关闭对应的CMD窗口
echo.
echo 📝 注意: Worker和Beat在独立的CMD窗口中运行
echo    关闭窗口即可停止对应服务
echo.
pause