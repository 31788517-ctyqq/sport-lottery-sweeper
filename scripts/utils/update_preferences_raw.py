import sqlite3
import json

conn = sqlite3.connect('data/sport_lottery.db')
c = conn.cursor()

# 首先检查表结构
c.execute("PRAGMA table_info(users)")
print("表结构:")
for col in c.fetchall():
    print(f"  {col}")

# 当前值
c.execute("SELECT username, notification_preferences FROM users")
rows = c.fetchall()
print("\n所有用户:")
for row in rows:
    print(f"  {row[0]}: {row[1]} (类型: {type(row[1])})")

# 更新所有用户的notification_preferences为有效的JSON空对象
print("\n更新所有用户...")
for row in rows:
    username = row[0]
    current = row[1]
    if isinstance(current, str):
        try:
            parsed = json.loads(current) if current.strip() else {}
            new_val = json.dumps(parsed)
            c.execute("UPDATE users SET notification_preferences = ? WHERE username = ?", (new_val, username))
            print(f"  已更新 {username}: {new_val}")
        except json.JSONDecodeError:
            # 如果不是有效JSON，设置为空对象
            c.execute("UPDATE users SET notification_preferences = ? WHERE username = ?", ('{}', username))
            print(f"  已修复 {username}: {{}}")
    else:
        # 如果不是字符串，可能是None或其他类型
        if current is None:
            c.execute("UPDATE users SET notification_preferences = ? WHERE username = ?", ('{}', username))
            print(f"  已设置 {username} 为空对象")
        else:
            # 尝试转换为JSON字符串
            try:
                new_val = json.dumps(current)
                c.execute("UPDATE users SET notification_preferences = ? WHERE username = ?", (new_val, username))
                print(f"  已转换 {username}: {new_val}")
            except:
                c.execute("UPDATE users SET notification_preferences = ? WHERE username = ?", ('{}', username))
                print(f"  已重置 {username}: {{}}")

conn.commit()

# 再次检查
c.execute("SELECT username, notification_preferences FROM users")
print("\n更新后:")
for row in c.fetchall():
    print(f"  {row[0]}: {row[1]}")

conn.close()