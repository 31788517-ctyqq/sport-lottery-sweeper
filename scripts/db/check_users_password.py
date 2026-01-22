import sqlite3
import os

def check_users_password():
    """检查users表中的用户密码"""
    db_path = 'sport_lottery.db'
    
    if not os.path.exists(db_path):
        print(f"数据库文件 {db_path} 不存在")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查users表结构
        cursor.execute("PRAGMA table_info(users);")
        columns = cursor.fetchall()
        print("users表结构:")
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
        
        # 检查users表中是否有admin用户
        cursor.execute("SELECT username, password_hash FROM users WHERE username = 'admin';")
        result = cursor.fetchone()
        
        if result:
            print(f"\n找到admin用户:")
            print(f"  用户名: {result[0]}")
            print(f"  密码哈希: {result[1]}")
        else:
            print("\nusers表中没有找到admin用户")
            
        # 列出所有用户
        cursor.execute("SELECT username, password_hash FROM users LIMIT 5;")
        users = cursor.fetchall()
        print(f"\nusers表中的前5个用户:")
        for user in users:
            print(f"  {user[0]}: {user[1][:20]}...")
            
        conn.close()
        
    except Exception as e:
        print(f"检查用户密码时出错: {e}")

if __name__ == "__main__":
    check_users_password()