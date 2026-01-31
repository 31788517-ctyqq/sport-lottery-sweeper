#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版错误收集脚本
绕过pytest的技术问题，直接收集业务错误
"""

import sys
import os
from datetime import datetime

def log_error(test_name, error_msg):
    """记录错误信息"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("error_collection.log", "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {test_name}: {error_msg}\n")

def test_imports():
    """测试基础导入"""
    print("=== 测试基础导入 ===")
    
    tests = [
        ("Backend路径设置", lambda: sys.path.insert(0, 'backend')),
        ("Base模型导入", lambda: __import__('core.database').Base),
        ("AdminUser模型", lambda: __import__('models.admin_user').AdminUser),
        ("Role模型", lambda: __import__('models.role').Role),
        ("数据库工具", lambda: __import__('database_utils').get_db_connection),
    ]
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"✅ {name}")
        except Exception as e:
            print(f"❌ {name}: {str(e)[:100]}")
            log_error("Import_Test", f"{name}: {str(e)}")

def test_database():
    """测试数据库"""
    print("\n=== 测试数据库 ===")
    
    try:
        import sqlite3
        db_path = "data/sport_lottery.db"
        if not os.path.exists(db_path):
            print(f"❌ 数据库文件不存在: {db_path}")
            log_error("Database_Test", f"数据库文件不存在: {db_path}")
            return
            
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM sqlite_master WHERE type="table";')
        tables = cursor.fetchall()
        print(f"✅ 数据库连接成功，发现 {len(tables)} 张表")
        
        # 检查关键表
        table_names = [t[0] for t in tables]
        key_tables = ['admin_users', 'roles', 'matches']
        for table in key_tables:
            if table in table_names:
                print(f"  ✅ {table} 表存在")
            else:
                print(f"  ❌ {table} 表缺失")
                log_error("Database_Test", f"缺失关键表: {table}")
        
        conn.close()
    except Exception as e:
        print(f"❌ 数据库测试失败: {str(e)}")
        log_error("Database_Test", str(e))

def test_api_endpoints():
    """测试API端点"""
    print("\n=== 测试API端点 ===")
    
    try:
        import requests
        
        # 测试基础端点
        endpoints = [
            ("基础API", "http://localhost:8000/"),
            ("健康检查", "http://localhost:8000/api/v1/auth/login"),
        ]
        
        for name, url in endpoints:
            try:
                if "login" in url:
                    # POST请求测试
                    response = requests.post(url, json={"username": "admin", "password": "admin123"}, timeout=5)
                else:
                    # GET请求测试  
                    response = requests.get(url, timeout=5)
                print(f"✅ {name}: {response.status_code}")
            except Exception as e:
                print(f"❌ {name}: {str(e)[:50]}")
                log_error("API_Test", f"{name}: {str(e)}")
                
    except ImportError:
        print("⚠️  requests库未安装，跳过API测试")
    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")
        log_error("API_Test", str(e))

def main():
    """主函数"""
    print("🔍 开始简化错误收集...")
    print(f"📁 工作目录: {os.getcwd()}")
    
    # 初始化日志文件
    with open("error_collection.log", "w", encoding="utf-8") as f:
        f.write(f"错误收集开始: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # 执行测试
    test_imports()
    test_database()
    test_api_endpoints()
    
    # 生成汇总
    print("\n=== 错误收集完成 ===")
    try:
        with open("error_collection.log", "r", encoding="utf-8") as f:
            errors = f.readlines()
        error_count = len([line for line in errors if "ERROR" in line or "❌" in line])
        print(f"📊 发现 {error_count} 个错误，详情见 error_collection.log")
    except:
        print("📄 错误日志已保存到 error_collection.log")

if __name__ == "__main__":
    main()
