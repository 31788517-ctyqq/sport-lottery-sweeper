import sqlite3
import sys

def main():
    db_path = "sport_lottery.db"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查看所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print("数据库中的表:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 检查admin_users表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='admin_users';")
        admin_users_table = cursor.fetchone()
        
        if admin_users_table:
            print("\nadmin_users表存在:")
            cursor.execute("SELECT * FROM admin_users;")
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    print(f"  {row}")
            else:
                print("  admin_users表为空")
        else:
            print("\nadmin_users表不存在")
            
        # 检查users表
        cursor.execute("SELECT * FROM users WHERE username='admin';")
        user = cursor.fetchone()
        print("\nusers表中的admin用户:")
        if user:
            print(f"  ID: {user[0]}, 用户名: {user[1]}, 邮箱: {user[2]}, 角色: {user[85]}, user_type: {user[89]}")
        else:
            print("  未找到admin用户")
            
        conn.close()
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()