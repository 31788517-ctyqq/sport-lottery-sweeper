"""
将100qiu数据源添加到test.db中
"""
import sqlite3
import json

def insert_100qiu_to_test_db():
    # 连接到test.db
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    # 检查是否已存在100qiu数据源
    cursor.execute("SELECT id FROM data_sources WHERE name = '100qiu竞彩基础数据'")
    existing = cursor.fetchone()

    if existing:
        print('100qiu数据源已存在')
    else:
        # 插入100qiu数据源
        config = {
            'params': {'dateTime': '26011'},
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'application/json, text/plain, */*',
                'Referer': 'https://m.100qiu.com/'
            },
            'method': 'GET',
            'data_source_type': 'hundred_qiu',
            'cron_expression': '0 2 * * *'
        }
        
        cursor.execute(
            'INSERT INTO data_sources (name, type, status, url, config, created_by, latitude, longitude, created_at, updated_at, priority) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
            ('100qiu竞彩基础数据', 'api', 1, 'https://m.100qiu.com/api/dcListBasic', json.dumps(config), 1, 0.0, 0.0, '2026-02-02 01:11:00', '2026-02-02 01:11:00', 1)
        )
        
        print('已将100qiu数据源添加到test.db')

    # 同样添加到crawler_configs表
    cursor.execute("SELECT id FROM crawler_configs WHERE name = '100qiu竞彩基础数据'")
    existing_config = cursor.fetchone()

    if existing_config:
        print('100qiu爬虫配置已存在')
    else:
        config_data = json.dumps({'data_source_type': 'hundred_qiu'})
        cursor.execute(
            'INSERT INTO crawler_configs (name, description, url, frequency, is_active, config_data, created_by) VALUES (?, ?, ?, ?, ?, ?, ?)',
            ('100qiu竞彩基础数据', '100qiu竞彩基础数据源的爬虫配置', 'https://m.100qiu.com/api/dcListBasic', 3600, 1, config_data, 1)
        )
        print('已将100qiu爬虫配置添加到test.db')

    # 为100qiu数据源创建任务
    cursor.execute("SELECT id FROM crawler_configs WHERE name = '100qiu竞彩基础数据'")
    config_row = cursor.fetchone()
    
    if config_row:
        config_id = config_row[0]
        cursor.execute("SELECT id FROM crawler_tasks WHERE source_id = ? AND name = '100qiu数据抓取任务'", (config_id,))
        existing_task = cursor.fetchone()
        
        if existing_task:
            print('100qiu数据抓取任务已存在')
        else:
            task_config = {
                "data_source_type": "hundred_qiu",
                "params": {
                    "dateTime": "26011"
                }
            }
            cursor.execute(
                'INSERT INTO crawler_tasks (name, source_id, task_type, cron_expression, is_active, status, config, created_by) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                ('100qiu数据抓取任务', config_id, 'crawl', '0 */2 * * *', 1, 'stopped', json.dumps(task_config), 1)
            )
            print('已将100qiu数据抓取任务添加到test.db')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    insert_100qiu_to_test_db()