#!/usr/bin/env python3
import sqlite3
from backend.core.security import get_password_hash

conn = sqlite3.connect('data/sport_lottery.db')
cursor = conn.cursor()

# 生成密码哈希
ph = get_password_hash('admin123')

# 插入管理员
cursor.execute('''
INSERT INTO admin_users 
(id, username, email, password_hash, real_name, phone, department, position, 
 role, status, two_factor_enabled, two_factor_secret, password_expires_at, 
 must_change_password, is_verified, failed_login_attempts, login_count, 
 created_by, remarks, preferences, created_at, updated_at) 
VALUES 
(1, 'admin', 'admin@example.com', ?, '系统管理员', '', '', '', 
 'admin', 'active', 0, '', NULL, 
 0, 1, 0, 0, 
 NULL, '', '{}', datetime('now'), datetime('now'))
''', (ph,))

conn.commit()

# 验证
cursor.execute('SELECT id, username, email, role FROM admin_users WHERE username=?', ('admin',))
result = cursor.fetchone()
print('创建结果:', result)

conn.close()
