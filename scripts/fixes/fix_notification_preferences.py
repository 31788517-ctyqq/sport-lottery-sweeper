import sqlite3
import json

conn = sqlite3.connect('sport_lottery.db')
c = conn.cursor()

# 检查notification_preferences列的值
c.execute("SELECT username, notification_preferences FROM users WHERE username='admin'")
admin = c.fetchone()
if admin:
    username = admin[0]
    pref_value = admin[1]
    print(f"用户名: {username}")
    print(f"notification_preferences原值: {pref_value}")
    print(f"类型: {type(pref_value)}")
    
    # 尝试解析为JSON
    new_value = "{}"
    if pref_value:
        try:
            # 如果已经是字典格式，确保它是有效的JSON
            parsed = json.loads(pref_value)
            print(f"✅ 可以解析为JSON: {parsed}")
            new_value = json.dumps(parsed)
        except json.JSONDecodeError:
            print(f"❌ 不是有效JSON，设置为空字典")
            new_value = "{}"
    else:
        print(f"值为空，设置为空字典")
        new_value = "{}"
    
    # 更新列
    c.execute("UPDATE users SET notification_preferences = ? WHERE username = 'admin'", (new_value,))
    print(f"更新了 {c.rowcount} 行")
    
    # 验证
    c.execute("SELECT notification_preferences FROM users WHERE username='admin'")
    updated = c.fetchone()[0]
    print(f"更新后值: {updated}")
    try:
        parsed = json.loads(updated)
        print(f"✅ 验证通过: {parsed}")
    except:
        print(f"❌ 验证失败")

conn.commit()
conn.close()
print("✅ 修复完成")