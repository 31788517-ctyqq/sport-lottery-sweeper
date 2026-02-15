import sqlite3

conn = sqlite3.connect('data/sport_lottery.db')
c = conn.cursor()

# 检查admin用户的created_at和updated_at值
c.execute("SELECT username, created_at, updated_at FROM users WHERE username='admin'")
admin = c.fetchone()
if admin:
    print(f"用户名: {admin[0]}")
    print(f"created_at: {admin[1]} (类型: {type(admin[1])})")
    print(f"updated_at: {admin[2]} (类型: {type(admin[2])})")
    
    # 尝试解析
    import datetime
    try:
        dt = datetime.datetime.fromisoformat(admin[1])
        print(f"可以解析为datetime: {dt}")
    except Exception as e:
        print(f"无法解析: {e}")

# 检查所有用户的created_at值
print("\n所有用户的created_at值:")
c.execute("SELECT username, created_at FROM users")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}")

conn.close()