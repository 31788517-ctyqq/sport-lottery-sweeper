import sqlite3

def check_admin_tables():
    expected_admin_tables = ['admin_users', 'departments', 'roles', 'permissions']
    
    try:
        conn = sqlite3.connect('data/sport_lottery.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        print("Admin模块表检查:")
        for table in expected_admin_tables:
            if table in existing_tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"  ✓ {table}: {count} 条记录")
            else:
                print(f"  ✗ {table}: 缺失")
        
        # 检查permissions表是否存在
        if 'permissions' not in existing_tables:
            print("\n缺失的permissions表可能导致权限相关功能异常")
            print("这可能影响：")
            print("  - 角色权限管理")
            print("  - 功能访问控制") 
            print("  - API端点授权")
        
        conn.close()
        
    except Exception as e:
        print(f"检查admin表时出错: {e}")

if __name__ == "__main__":
    check_admin_tables()