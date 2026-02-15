import sqlite3

def check_database():
    try:
        # 连接到根目录的数据库文件
        conn = sqlite3.connect('data/sport_lottery.db')
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        print("Tables in database:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # 检查admin_users表
        if ('admin_users',) in tables:
            cursor.execute("SELECT username, status FROM admin_users")
            admin_users = cursor.fetchall()
            print("\nAdmin users:")
            for user in admin_users:
                print(f"  - Username: {user[0]}, Status: {user[1]}")
        else:
            print("\nNo admin_users table found")
            
        conn.close()
        print(f"\nDatabase file location: sport_lottery.db")
        
    except Exception as e:
        print(f"Error checking database: {e}")

if __name__ == "__main__":
    check_database()