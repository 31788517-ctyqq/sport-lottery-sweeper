#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sqlite3

conn = sqlite3.connect('data/sport_lottery.db')
cursor = conn.cursor()

# 检查是否已存在
source_name = "500.com足球竞彩"
cursor.execute("SELECT id FROM crawler_configs WHERE source_name = ?", (source_name,))
if cursor.fetchone():
    print("500.com配置已存在，跳过插入")
else:
    cursor.execute(
        "INSERT INTO crawler_configs (source_name, url_pattern, interval, enabled) VALUES (?, ?, ?, ?)",
        (source_name, "https://trade.500.com/jczq/", 4, 1)
    )
    conn.commit()
    print("✅ 500.com爬虫配置已成功插入数据库")

conn.close()
