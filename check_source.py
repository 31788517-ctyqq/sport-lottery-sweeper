import sqlite3
import json

conn = sqlite3.connect('data/sport_lottery.db')
cursor = conn.cursor()

# 检查数据源ID 9的配置
cursor.execute('SELECT id, name, type, config FROM data_sources WHERE id = 9')
row = cursor.fetchone()
if row:
    id, name, type, config_str = row
    print('数据源 ID {}:'.format(id))
    print('  名称: {}'.format(name))
    print('  类型: {}'.format(type))
    print('  配置字符串: {}'.format(config_str))
    
    try:
        config = json.loads(config_str)
        print('  配置解析: {}'.format(json.dumps(config, indent=2, ensure_ascii=False)))
        print('  date_time字段: {}'.format(config.get('date_time', '未找到')))
    except Exception as e:
        print('  配置解析失败: {}'.format(e))
else:
    print('未找到数据源ID 9')

# 检查所有100qiu数据源
print('\n=== 所有100qiu数据源 ===')
cursor.execute('SELECT id, name, type, config FROM data_sources WHERE type = "100qiu" OR name LIKE "%100qiu%"')
rows = cursor.fetchall()
for row in rows:
    id, name, type, config_str = row
    print(f'ID {id}: {name} (类型: {type})')
    try:
        config = json.loads(config_str)
        print(f'  date_time: {config.get("date_time", "未找到")}')
    except:
        pass

conn.close()