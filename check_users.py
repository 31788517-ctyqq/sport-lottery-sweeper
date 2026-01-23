import sqlite3

def check_users():
    conn = sqlite3.connect('sport_lottery.db')
    cursor = conn.cursor()
    
    # 查询所有用户
    cursor.execute("SELECT id, username, email, role, status FROM users;")
    users = cursor.fetchall()
    print('数据库中的用户:')
    for user in users:
        print(f"- ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Role: {user[3]}, Status: {user[4]}")
    
    # 特别查询admin用户
    cursor.execute("SELECT id, username, email, role, status, password_hash FROM users WHERE username='admin';")
    admin_users = cursor.fetchall()
    print('\nAdmin用户:')
    for user in admin_users:
        print(f"- ID: {user[0]}, Username: {user[1]}, Email: {user[2]}, Role: {user[3]}, Status: {user[4]}")
        print(f"- Password hash exists: {'Yes' if user[5] else 'No'}")
    
    conn.close()

if __name__ == "__main__":
    check_users()