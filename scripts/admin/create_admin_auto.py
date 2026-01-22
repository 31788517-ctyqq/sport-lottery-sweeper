import sqlite3
import bcrypt

def get_column_default(col_type, col_name):
    """根据列类型和名称返回合适的默认值"""
    col_type = col_type.upper()
    
    # 特殊列处理
    if col_name in ['followers_count', 'following_count', 'login_count', 'failed_login_attempts']:
        return 0
    if col_name in ['is_verified', 'is_online', 'is_superuser', 'is_active']:
        return 1 if col_name == 'is_superuser' else 0
    if col_name in ['status']:
        return 'active'
    if col_name in ['role']:
        return 'user'
    if col_name in ['user_type']:
        return 'admin'
    if col_name in ['timezone']:
        return 'UTC'
    if col_name in ['language']:
        return 'zh'
    if col_name in ['notification_preferences']:
        return '{}'
    
    # 根据类型处理
    if 'INT' in col_type or 'BOOL' in col_type:
        return 0
    elif 'TEXT' in col_type or 'VARCHAR' in col_type:
        return ''
    elif 'DATETIME' in col_type or 'TIMESTAMP' in col_type:
        return 'datetime("now")'
    elif 'DATE' in col_type:
        return 'date("now")'
    else:
        return None

def create_admin():
    conn = sqlite3.connect('sport_lottery.db')
    c = conn.cursor()
    
    # 检查是否已存在
    c.execute("SELECT username FROM users WHERE username='admin'")
    if c.fetchone():
        print("admin用户已存在")
        conn.close()
        return True
    
    # 获取列信息
    c.execute('PRAGMA table_info(users)')
    columns = c.fetchall()
    
    print(f"表 'users' 有 {len(columns)} 列")
    
    # 准备列名和值
    col_names = []
    values = []
    
    for col in columns:
        col_name = col[1]
        col_type = col[2]
        not_null = col[3]
        has_default = col[4] is not None
        
        col_names.append(col_name)
        
        # 根据列名设置值
        if col_name == 'username':
            values.append('admin')
        elif col_name == 'email':
            values.append('admin@example.com')
        elif col_name == 'password_hash':
            password = 'admin123'
            hash_val = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            values.append(hash_val)
        elif col_name == 'first_name':
            values.append('系统')
        elif col_name == 'last_name':
            values.append('管理员')
        elif col_name == 'nickname':
            values.append('Admin')
        elif col_name == 'role':
            values.append('admin')
        elif col_name == 'status':
            values.append('active')
        elif col_name == 'is_verified':
            values.append(1)
        elif col_name == 'is_online':
            values.append(0)
        elif col_name == 'user_type':
            values.append('admin')
        elif col_name == 'timezone':
            values.append('UTC')
        elif col_name == 'language':
            values.append('zh')
        elif col_name == 'notification_preferences':
            values.append('{}')
        elif col_name == 'login_count':
            values.append(0)
        elif col_name == 'id':
            # 自增，用NULL
            values.append(None)
        elif col_name == 'created_at':
            values.append('datetime("now")')
        elif col_name == 'updated_at':
            values.append('datetime("now")')
        else:
            # 其他列，根据是否可为空设置默认值
            if not_null:
                default_val = get_column_default(col_type, col_name)
                values.append(default_val)
            else:
                values.append(None)
    
    # 构建INSERT语句
    cols_str = ', '.join([name for name in col_names])
    placeholders = ', '.join(['?' for _ in range(len(col_names))])
    
    sql = f'INSERT INTO users ({cols_str}) VALUES ({placeholders})'
    
    print("执行的SQL:", sql)
    print("值:", values)
    
    try:
        c.execute(sql, values)
        conn.commit()
        print("admin用户创建成功!")
        
        # 验证
        c.execute("SELECT username, role, status FROM users WHERE username='admin'")
        row = c.fetchone()
        print(f"   验证: {row}")
        return True
    except Exception as e:
        print(f"创建失败: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    create_admin()