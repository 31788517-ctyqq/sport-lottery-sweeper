@echo off
echo ========================================
echo 用户管理系统 - 快速启动脚本
echo ========================================
echo.

echo [步骤 1/4] 检查并生成模拟数据...
cd /d "%~dp0"
python scripts/simple_mock_users.py create
if %errorlevel% neq 0 (
    echo 警告: 模拟数据生成可能失败，继续启动服务...
)
echo.

echo [步骤 2/4] 启动后端服务...
cd backend
start "Sport Lottery Backend" cmd /k "python main.py"
echo 后端服务已启动，请等待几秒...
timeout /t 3 /nobreak > nul
echo.

echo [步骤 3/4] 启动前端服务...
cd ..\frontend
start "Sport Lottery Frontend" cmd /k "pnpm dev"
echo 前端服务已启动，请等待几秒...
timeout /t 3 /nobreak > nul
echo.

echo ========================================
echo 服务启动完成！
echo ========================================
echo.
echo 访问地址:
echo   - 前端主页:     http://localhost:3000
echo   - 后台用户管理: http://localhost:3000/admin-users
echo   - 前台用户管理: http://localhost:3000/frontend-users
echo   - API文档:      http://localhost:8000/docs
echo.
echo 测试账号:
echo   - 用户名: sa_mock_data_2026_01_19
echo   - 密码:   SuperAdmin@123456
echo.
echo 如需停止服务，请关闭打开的命令行窗口。
echo.
pause
