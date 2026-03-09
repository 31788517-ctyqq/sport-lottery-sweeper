@echo off
cd /d "%~dp0"

:: 使用统一的数据库位置
set DB_PATH=../data/sport_lottery.db

:: 转换为绝对路径
for %%i in ("%DB_PATH%") do set DB_PATH=%%~fi

if not exist "%DB_PATH%" (
    echo ❌ 数据库文件不存在: %DB_PATH%
    echo 请先运行数据库初始化脚本
    pause
    exit /b 1
)

echo 使用数据库: %DB_PATH%
echo.

python -c "import sqlite3; conn = sqlite3.connect(r'%DB_PATH%'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM admin_users'); print('后台用户总数:', cursor.fetchone()[0]); cursor.execute('SELECT COUNT(*) FROM users'); print('前台用户总数:', cursor.fetchone()[0]); cursor.execute('SELECT COUNT(*) FROM admin_operation_logs'); print('操作日志数:', cursor.fetchone()[0]); cursor.execute('SELECT COUNT(*) FROM admin_login_logs'); print('登录日志数:', cursor.fetchone()[0]); cursor.execute('SELECT username, role, status FROM admin_users LIMIT 3'); print('\\n后台用户示例:'); [print(f'  - {row[0]} ({row[1]}, {row[2]})') for row in cursor.fetchall()]; conn.close()"
pause
