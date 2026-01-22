"""
检查用户脚本
"""
import sqlite3

def check_admin_user():
    conn = sqlite3.connect('sport_lottery.db')
    cursor = conn.cursor()
    cursor.execute("SELECT username, password_hash FROM users WHERE username = 'admin'")
    result = cursor.fetchone()
    if result:
        print(f"User: {result[0]}")
        print(f"Hash: {result[1]}")
    else:
        print("Admin user not found")
    conn.close()

if __name__ == "__main__":
    check_admin_user()