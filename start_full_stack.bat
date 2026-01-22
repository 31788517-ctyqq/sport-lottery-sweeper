@echo off
chcp 65001 > nul
cd /d %~dp0

echo ╔════════════════════════════════════════════════════════════╗
echo ║     🚀 竞彩足球赛程系统 - 全栈启动脚本                    ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo 📋 系统检查...
echo ────────────────────────────────────────────────────────────

:: 检查Python
python --version > nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)
echo ✅ Python已安装

:: 检查Node.js
node --version > nul 2>&1
if errorlevel 1 (
    echo ❌ 未找到Node.js，请先安装Node.js
    pause
    exit /b 1
)
echo ✅ Node.js已安装

:: 检查数据文件
if not exist "debug\500_com_matches_*.json" (
    echo ⚠️  未找到数据文件，正在运行爬虫...
    python crawl_500_com.py
)

echo.
echo ════════════════════════════════════════════════════════════
echo 🎯 启动服务
echo ════════════════════════════════════════════════════════════
echo.

:: 启动后端（在新窗口）
echo 🔷 启动后端服务器 (http://localhost:8000)...
start "后端服务器" cmd /k "cd /d %~dp0 && echo 🔷 后端服务器启动中... && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload"

:: 等待后端启动
echo ⏳ 等待后端启动 (5秒)...
timeout /t 5 /nobreak > nul

:: 启动前端（在新窗口）
echo 🔶 启动前端开发服务器...
start "前端服务器" cmd /k "cd /d %~dp0\frontend && echo 🔶 前端服务器启动中... && npm run dev"

echo.
echo ════════════════════════════════════════════════════════════
echo ✅ 启动完成！
echo ════════════════════════════════════════════════════════════
echo.
echo 📍 访问地址:
echo    - 前端页面: http://localhost:5173/#/jczq-schedule
echo    - 后端API:  http://localhost:8000/api/v1/jczq/matches?source=500
echo    - API文档:  http://localhost:8000/docs
echo.
echo 💡 提示:
echo    - 两个服务器窗口将保持打开状态
echo    - 关闭窗口即可停止相应服务
echo    - 按 Ctrl+C 可以停止服务
echo.
echo 🎉 竞彩足球赛程系统已就绪！
echo ════════════════════════════════════════════════════════════
echo.

:: 等待5秒后自动打开浏览器
timeout /t 5 /nobreak > nul
start http://localhost:5173/#/jczq-schedule

echo 已自动打开浏览器...
echo.
pause
