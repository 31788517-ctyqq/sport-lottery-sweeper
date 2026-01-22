#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
创建缺失的数据库表
"""
import sqlite3
import os

def create_tables():
    db_path = 'sport_lottery.db'
    if not os.path.exists(db_path):
        print(f'✗ 数据库文件不存在: {db_path}')
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        # 检查现有表
        c.execute('SELECT name FROM sqlite_master WHERE type="table";')
        existing_tables = [row[0] for row in c.fetchall()]
        print(f'现有表: {existing_tables}')
        
        # 需要创建的表
        tables_to_create = {
            'system_configs': '''
                CREATE TABLE system_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key VARCHAR(100) UNIQUE NOT NULL,
                    value VARCHAR(500),
                    description VARCHAR(300),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'crawler_configs': '''
                CREATE TABLE crawler_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_name VARCHAR(100) NOT NULL,
                    url_pattern VARCHAR(500) NOT NULL,
                    interval INTEGER DEFAULT 60,
                    enabled BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''',
            'intelligence_records': '''
                CREATE TABLE intelligence_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    model VARCHAR(100) NOT NULL,
                    accuracy VARCHAR(20),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status VARCHAR(20) DEFAULT '完成'
                )
            '''
        }
        
        # 创建缺失的表
        for table_name, sql in tables_to_create.items():
            if table_name not in existing_tables:
                print(f'创建表: {table_name}')
                c.execute(sql)
                print(f'✓ {table_name}表创建成功')
            else:
                print(f'✓ {table_name}表已存在')
        
        conn.commit()
        conn.close()
        print('\n✓ 所有表创建完成!')
        return True
        
    except Exception as e:
        print(f'✗ 错误: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    create_tables()