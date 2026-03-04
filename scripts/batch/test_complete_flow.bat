@echo off
chcp 65001 > nul
cd /d %~dp0

echo ╔════════════════════════════════════════════════════════════╗
echo ║     🧪 完整流程测试                                        ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo 1️⃣ 测试爬虫功能
echo ════════════════════════════════════════════════════════════
python crawl_500_com.py
if errorlevel 1 (
    echo ❌ 爬虫测试失败
    pause
    exit /b 1
)
echo ✅ 爬虫测试成功
echo.

echo 2️⃣ 检查数据文件
echo ════════════════════════════════════════════════════════════
dir /b debug\500_com_matches_*.json | findstr "500_com_matches_"
if errorlevel 1 (
    echo ❌ 数据文件不存在
    pause
    exit /b 1
)
echo ✅ 数据文件存在
echo.

echo 3️⃣ 启动后端服务器（按Ctrl+C停止）
echo ════════════════════════════════════════════════════════════
echo 🔷 后端将在 http://localhost:8000 启动
echo 🔷 API端点: http://localhost:8000/api/v1/jczq/matches?source=500
echo 🔷 API文档: http://localhost:8000/docs
echo.
echo 💡 启动后，请在浏览器中测试以下链接：
echo    http://localhost:8000/api/v1/jczq/matches?source=500
echo.
echo 按任意键启动后端服务器...
pause > nul

python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
