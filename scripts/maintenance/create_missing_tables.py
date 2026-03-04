#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建缺失的关键表：爬虫日志表和IP池测试数据
AI_WORKING: system @2026-02-14 - 补充数据库表结构
"""

import sqlite3
import json
from datetime import datetime, timedelta
import random

DB_PATH = 'data/sport_lottery.db'

def create_crawler_logs_tables():
    """创建爬虫日志相关表"""
    print("【步骤1】创建爬虫日志表...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查外键表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crawler_configs'")
    if not cursor.fetchone():
        print("⚠ crawler_configs表不存在，先创建基础表结构")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crawler_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                type VARCHAR(50) NOT NULL,
                url VARCHAR(500),
                config TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # 插入一个默认配置
        cursor.execute('''
            INSERT INTO crawler_configs (name, type, url, config) 
            VALUES ('default', 'api', 'https://example.com', '{}')
        ''')
        print("[OK] crawler_configs表创建完成")
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crawler_tasks'")
    if not cursor.fetchone():
        print("⚠ crawler_tasks表不存在，创建基础表结构")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crawler_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                source_id INTEGER,
                task_type VARCHAR(50) DEFAULT 'DATA_COLLECTION',
                status VARCHAR(20) DEFAULT 'pending',
                cron_expression VARCHAR(100),
                is_active BOOLEAN DEFAULT 1,
                run_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                error_count INTEGER DEFAULT 0,
                config TEXT DEFAULT '{}',
                created_by INTEGER DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("[OK] crawler_tasks表创建完成")
    
    # 创建crawler_task_logs表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crawler_task_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            source_id INTEGER NOT NULL,
            status VARCHAR(20) NOT NULL,
            started_at DATETIME NOT NULL,
            completed_at DATETIME,
            duration_seconds REAL,
            records_processed INTEGER,
            records_success INTEGER,
            records_failed INTEGER,
            error_message TEXT,
            error_details TEXT,
            response_time_ms REAL,
            created_by INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建crawler_source_stats表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS crawler_source_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_id INTEGER NOT NULL,
            date DATE NOT NULL,
            total_requests INTEGER DEFAULT 0,
            successful_requests INTEGER DEFAULT 0,
            failed_requests INTEGER DEFAULT 0,
            avg_response_time_ms REAL,
            total_records INTEGER DEFAULT 0,
            last_success_at DATETIME,
            last_failure_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_crawler_task_logs_task_id ON crawler_task_logs(task_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_crawler_task_logs_source_id ON crawler_task_logs(source_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_crawler_task_logs_status ON crawler_task_logs(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_crawler_task_logs_started_at ON crawler_task_logs(started_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_crawler_source_stats_source_id ON crawler_source_stats(source_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_crawler_source_stats_date ON crawler_source_stats(date)')
    
    conn.commit()
    print("[OK] 爬虫日志表创建完成")
    conn.close()

def create_test_log_data():
    """创建测试日志数据"""
    print("\n【步骤2】创建测试日志数据...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取现有的source_id和task_id
    cursor.execute('SELECT id FROM crawler_configs LIMIT 1')
    source_result = cursor.fetchone()
    source_id = source_result[0] if source_result else 1
    
    cursor.execute('SELECT id FROM crawler_tasks LIMIT 1')
    task_result = cursor.fetchone()
    if not task_result:
        # 创建一个测试任务
        cursor.execute('''
            INSERT INTO crawler_tasks (name, source_id, status) 
            VALUES ('测试任务', ?, 'completed')
        ''', (source_id,))
        task_id = cursor.lastrowid
    else:
        task_id = task_result[0]
    
    # 生成测试日志数据
    statuses = ['completed', 'failed', 'running']
    base_time = datetime.now() - timedelta(days=7)
    
    for i in range(50):
        started_at = base_time + timedelta(hours=i*3)
        status = random.choice(statuses)
        
        if status == 'completed':
            completed_at = started_at + timedelta(minutes=random.randint(1, 10))
            duration = (completed_at - started_at).total_seconds()
            records_processed = random.randint(10, 100)
            records_success = random.randint(records_processed-5, records_processed)
            records_failed = records_processed - records_success
            error_message = None
        elif status == 'failed':
            completed_at = started_at + timedelta(minutes=random.randint(1, 5))
            duration = (completed_at - started_at).total_seconds()
            records_processed = random.randint(5, 50)
            records_success = 0
            records_failed = records_processed
            error_message = random.choice(['网络超时', '解析失败', '数据源不可用', 'IP被封禁'])
        else:  # running
            completed_at = None
            duration = None
            records_processed = random.randint(1, 20)
            records_success = random.randint(0, records_processed)
            records_failed = records_processed - records_success
            error_message = None
        
        cursor.execute('''
            INSERT INTO crawler_task_logs 
            (task_id, source_id, status, started_at, completed_at, duration_seconds,
             records_processed, records_success, records_failed, error_message, response_time_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_id, source_id, status, started_at.strftime('%Y-%m-%d %H:%M:%S'),
            completed_at.strftime('%Y-%m-%d %H:%M:%S') if completed_at else None,
            duration, records_processed, records_success, records_failed,
            error_message, random.randint(100, 5000)
        ))
    
    # 创建数据源统计
    for i in range(7):
        date_val = (base_time + timedelta(days=i)).date()
        cursor.execute('''
            INSERT OR REPLACE INTO crawler_source_stats 
            (source_id, date, total_requests, successful_requests, failed_requests,
             avg_response_time_ms, total_records, last_success_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            source_id, date_val.strftime('%Y-%m-%d'),
            random.randint(50, 200), random.randint(40, 180), random.randint(0, 20),
            random.randint(200, 2000), random.randint(100, 500),
            (base_time + timedelta(days=i, hours=12)).strftime('%Y-%m-%d %H:%M:%S')
        ))
    
    conn.commit()
    print(f"[OK] 创建了50条任务日志和7天的统计数据")
    conn.close()

def create_test_ip_pool_data():
    """创建测试IP池数据"""
    print("\n【步骤3】创建测试IP池数据...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查是否已有数据
    cursor.execute('SELECT COUNT(*) FROM ip_pools')
    if cursor.fetchone()[0] > 0:
        print("[OK] IP池已有数据，跳过创建")
        conn.close()
        return
    
    # 生成测试IP池数据
    protocols = ['http', 'https', 'socks5']
    locations = ['美国', '日本', '新加坡', '德国', '英国', '加拿大', '澳大利亚', '韩国']
    anonymity_levels = ['透明', '匿名', '高匿']
    sources = ['免费采集', '付费购买', '自建爬取', '第三方API']
    statuses = ['active', 'inactive', 'testing']
    
    base_ip = [192, 168, 1]
    
    for i in range(100):
        # 生成IP地址
        ip_suffix = f"{base_ip[0]}.{base_ip[1]}.{base_ip[2]}.{i+1}"
        port = random.choice([8080, 3128, 8888, 1080, 7890, 9999, 10808, 10809])
        protocol = random.choice(protocols)
        location = random.choice(locations)
        status = random.choice(statuses)
        anonymity = random.choice(anonymity_levels)
        source = random.choice(sources)
        
        # 生成统计数据
        success_count = random.randint(0, 1000)
        failure_count = random.randint(0, 100)
        latency = random.randint(50, 2000)
        success_rate = int((success_count / (success_count + failure_count)) * 100) if (success_count + failure_count) > 0 else 0
        
        # 时间字段
        last_used = datetime.now() - timedelta(hours=random.randint(0, 72))
        last_checked = datetime.now() - timedelta(minutes=random.randint(1, 1440))
        
        # 禁用时间（部分IP可能被禁用）
        banned_until = None
        if random.random() < 0.1:  # 10%概率被禁用
            banned_until = datetime.now() + timedelta(hours=random.randint(1, 24))
        
        cursor.execute('''
            INSERT INTO ip_pools 
            (ip, port, protocol, location, status, remarks, success_count, failure_count,
             last_used, latency_ms, success_rate, last_checked, source, anonymity, score, banned_until)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ip_suffix, port, protocol, location, status,
            f'测试代理服务器-{i+1}', success_count, failure_count,
            last_used.strftime('%Y-%m-%d %H:%M:%S'), latency, success_rate,
            last_checked.strftime('%Y-%m-%d %H:%M:%S'), source, anonymity,
            random.randint(1, 100), 
            banned_until.strftime('%Y-%m-%d %H:%M:%S') if banned_until else None
        ))
    
    conn.commit()
    print(f"[OK] 创建了100条IP池测试数据")
    conn.close()

def create_test_ai_logs():
    """创建AI日志测试数据"""
    print("\n【步骤4】创建AI日志测试数据...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查log_entries表是否有数据
    cursor.execute('SELECT COUNT(*) FROM log_entries')
    if cursor.fetchone()[0] > 0:
        print("[OK] 日志表已有数据，跳过创建")
        conn.close()
        return
    
    # 生成AI日志数据
    levels = ['INFO', 'WARNING', 'ERROR', 'DEBUG']
    modules = ['auth', 'crawler', 'api', 'database', 'ai_service', 'user_management']
    messages = [
        '用户登录成功', '数据源连接失败', 'API请求超时', '数据库查询完成',
        'AI分析任务开始', '缓存命中', '任务执行完成', '权限验证通过',
        '网络连接异常', '数据解析成功', '批量插入完成', '会话创建成功'
    ]
    paths = ['/api/v1/login', '/api/v1/crawler/start', '/api/v1/data/query', '/admin/users']
    
    base_time = datetime.now() - timedelta(days=3)
    
    for i in range(200):
        timestamp = base_time + timedelta(minutes=i*10)
        level = random.choice(levels)
        module = random.choice(modules)
        message = random.choice(messages)
        
        cursor.execute('''
            INSERT INTO log_entries 
            (timestamp, level, module, message, user_id, ip_address, user_agent,
             session_id, request_path, response_status, duration_ms, extra_data)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            timestamp.strftime('%Y-%m-%d %H:%M:%S'), level, module, message,
            random.randint(1, 10) if random.random() > 0.3 else None,
            f"192.168.1.{random.randint(1, 254)}",
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            f"session_{random.randint(1000, 9999)}",
            random.choice(paths),
            random.choice([200, 201, 400, 401, 403, 404, 500]),
            random.randint(10, 5000),
            json.dumps({'trace_id': f'trace_{i}', 'batch_size': random.randint(1, 100)}, ensure_ascii=False)
        ))
    
    conn.commit()
    print(f"[OK] 创建了200条AI日志测试数据")
    conn.close()

def verify_tables():
    """验证表创建结果"""
    print("\n【步骤5】验证表创建结果...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查所有关键表
    key_tables = ['log_entries', 'ip_pools', 'crawler_task_logs', 'crawler_source_stats', 'sp_modification_logs']
    
    print("关键表状态:")
    for table in key_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  [OK] {table}: {count} 条记录")
    
    # 检查表结构
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    all_tables = [row[0] for row in cursor.fetchall()]
    print(f"\n数据库中共有 {len(all_tables)} 张表")
    
    conn.close()

if __name__ == '__main__':
    print("=" * 80)
    print("执行数据库迁移：创建缺失的日志和IP池表及测试数据")
    print("=" * 80)
    
    try:
        create_crawler_logs_tables()
        create_test_log_data()
        create_test_ip_pool_data()
        create_test_ai_logs()
        verify_tables()
        
        print("\n" + "=" * 80)
        print("[SUCCESS] 数据库迁移完成！所有关键表和数据已创建")
        print("=" * 80)
    except Exception as e:
        print(f"\n[ERROR] 迁移失败: {e}")
        import traceback
        traceback.print_exc()