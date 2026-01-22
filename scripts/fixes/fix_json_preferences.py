import sqlite3
import json

def fix():
    conn = sqlite3.connect('sport_lottery.db')
    c = conn.cursor()
    
    # 检查当前值
    c.execute("SELECT username, notification_preferences, typeof(notification_preferences) FROM users WHERE username='admin'")
    row = c.fetchone()
    if row:
        print(f"当前值: 用户名={row[0]}, 偏好={row[1]}, 类型={row[2]}")
    
    # 如果是字符串，尝试解析为JSON
    if row and isinstance(row[1], str):
        try:
            parsed = json.loads(row[1]) if row[1].strip() else {}
            print(f"解析为JSON: {parsed}")
            # 更新为JSON字符串（使用json.dumps确保有效）
            new_value = json.dumps(parsed)
            c.execute("UPDATE users SET notification_preferences = ? WHERE username='admin'", (new_value,))
            conn.commit()
            print("已更新notification_preferences为JSON字符串")
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            # 如果是空字符串，设置为空对象
            if row[1].strip() == '':
                new_value = '{}'
                c.execute("UPDATE users SET notification_preferences = ? WHERE username='admin'", (new_value,))
                conn.commit()
                print("已设置为空对象")
    else:
        print("notification_preferences不是字符串或用户不存在")
    
    # 再次检查
    c.execute("SELECT username, notification_preferences, typeof(notification_preferences) FROM users WHERE username='admin'")
    row = c.fetchone()
    if row:
        print(f"修复后: 用户名={row[0]}, 偏好={row[1]}, 类型={row[2]}")
    
    conn.close()

if __name__ == '__main__':
    fix()