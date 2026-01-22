import sqlite3
import bcrypt

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
        col_type = col[2].upper()
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
        elif col_name in ['created_by', 'updated_by', 'deleted_by']:
            values.append(None)
        else:
            # 其他列设为NULL
            values.append(None)
    
    # 构建INSERT语句
    cols_str = ', '.join([name for name in col_names])
    placeholders = ', '.join(['?' for _ in range(len(col_names))])
    
    sql = f'INSERT INTO users ({cols_str}) VALUES ({placeholders})'
    
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