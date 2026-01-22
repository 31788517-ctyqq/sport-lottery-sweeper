@echo off
cd /d "%~dp0"
python -c "import sqlite3; conn = sqlite3.connect('sport_lottery.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM admin_users'); print('后台用户总数:', cursor.fetchone()[0]); cursor.execute('SELECT COUNT(*) FROM users'); print('前台用户总数:', cursor.fetchone()[0]); cursor.execute('SELECT COUNT(*) FROM admin_operation_logs'); print('操作日志数:', cursor.fetchone()[0]); cursor.execute('SELECT COUNT(*) FROM admin_login_logs'); print('登录日志数:', cursor.fetchone()[0]); cursor.execute('SELECT username, role, status FROM admin_users LIMIT 3'); print('\n后台用户示例:'); [print(f'  - {row[0]} ({row[1]}, {row[2]})') for row in cursor.fetchall()]; conn.close()"
pause
