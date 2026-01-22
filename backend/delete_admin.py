import sqlite3

# 连接到数据库
conn = sqlite3.connect('sport_lottery.db')
cursor = conn.cursor()

# 删除admin用户
cursor.execute("DELETE FROM users WHERE username = 'admin'")
conn.commit()

print(f"Deleted {cursor.rowcount} admin user(s)")

# 关闭连接
conn.close()