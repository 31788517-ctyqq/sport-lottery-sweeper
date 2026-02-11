#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试文件：包含硬编码数据库路径，用于验证CI/CD检查
"""

import sqlite3

# 硬编码数据库路径 - 这应该被CI/CD检查捕获
conn = sqlite3.connect('sport_lottery.db')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM users')
print("Hardcoded path test")
conn.close()

# 另一个硬编码路径示例
def test_function():
    # 这里也有硬编码路径
    db_path = 'backend/sport_lottery.db'
    conn2 = sqlite3.connect(db_path)
    conn2.close()