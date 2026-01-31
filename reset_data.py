#!/usr/bin/env python3
"""
重新开始 - 清理数据并重新创建
"""
import sqlite3
from datetime import datetime
import json

print("="*70)
print("🔄 重新开始 - 体育彩票扫盘系统数据初始化")
print("="*70)

# 连接数据库
conn = sqlite3.connect('backend/sport_lottery.db')
cursor = conn.cursor()

# 1. 清空现有数据
print("\n1️⃣ 清空现有比赛数据...")
cursor.execute('DELETE FROM football_matches')
print("✓ 已清空football_matches表")

# 2. 创建数据源（如果不存在）
print("\n2️⃣ 创建/更新500万彩票数据源...")
cursor.execute("SELECT id FROM data_sources WHERE name='500万彩票'")
if not cursor.fetchone():
    source_config = {
        "baseUrl": "https://trade.500.com/jczq/",
        "description": "500万彩票网竞彩足球比赛数据源",
        "category": "竞彩赛程",
        "auto_crawl": True,
        "priority": "high"
    }
    
    cursor.execute("""
    INSERT INTO data_sources (name, type, status, url, config, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        "500万彩票", "api", 1, "https://trade.500.com/jczq/",
        json.dumps(source_config, ensure_ascii=False),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))
    print("✓ 创建500万彩票数据源")
else:
    print("✓ 数据源已存在")

# 3. 插入比赛数据（使用正确的竞彩编号格式）
print("\n3️⃣ 插入比赛数据（使用竞彩编号格式：周一001, 周二001...）")

matches = [
    # 周一比赛
    ('周一001', '北京国安', '上海申花', '2026-01-27 19:35:00', '中超', '未开始', 2.15, 3.20, 2.85, 8500),
    ('周一002', '山东泰山', '广州恒大', '2026-01-27 20:00:00', '中超', '未开始', 1.95, 3.40, 3.10, 9200),
    ('周一003', '曼联', '利物浦', '2026-01-27 22:00:00', '英超', '未开始', 2.60, 3.30, 2.45, 15600),
    ('周一004', '大阪钢巴', '浦和红钻', '2026-01-27 18:00:00', '日职联', '未开始', 2.65, 3.10, 2.40, 4300),
    # 周二比赛
    ('周二001', '江苏苏宁', '河南建业', '2026-01-28 15:30:00', '中超', '未开始', 2.40, 3.15, 2.60, 6800),
    ('周二002', '天津泰达', '重庆当代', '2026-01-28 19:35:00', '中超', '未开始', 2.80, 3.05, 2.35, 5400),
    ('周二003', '切尔西', '阿森纳', '2026-01-28 00:30:00', '英超', '未开始', 2.35, 3.45, 2.55, 18900),
    ('周二004', '皇马', '巴萨', '2026-01-28 03:00:00', '西甲', '未开始', 2.20, 3.60, 2.70, 24300),
    # 周三比赛
    ('周三001', '武汉卓尔', '石家庄永昌', '2026-01-29 19:35:00', '中超', '未开始', 2.10, 3.25, 2.90, 7200),
    ('周三002', '拜仁', '多特', '2026-01-29 04:00:00', '德甲', '未开始', 1.85, 3.75, 3.20, 16700),
]

inserted = 0
for match in matches:
    cursor.execute('''
    INSERT INTO football_matches 
    (match_id, home_team, away_team, match_time, league, status, 
     odds_home_win, odds_draw, odds_away_win, popularity, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
    ''', match)
    inserted += 1

conn.commit()
print(f"✓ 成功插入 {inserted} 场比赛")

# 4. 验证数据
print("\n4️⃣ 数据验证:")
print("-" * 90)
print(f"{'编号':<8} {'主队':<10} {'客队':<10} {'时间':<16} {'联赛':<8} {'胜':<6} {'平':<6} {'负':<6} {'热度':<6}")
print("-" * 90)

cursor.execute("SELECT match_id, home_team, away_team, match_time, league, odds_home_win, odds_draw, odds_away_win, popularity FROM football_matches ORDER BY match_time")
for row in cursor.fetchall():
    print(f"{row[0]:<8} {row[1]:<10} {row[2]:<10} {row[3]:<16} {row[4]:<8} {row[5]:<6.2f} {row[6]:<6.2f} {row[7]:<6.2f} {row[8]:<6}")

# 5. 检查数据库中的数据源
print("\n5️⃣ 数据源验证:")
cursor.execute("SELECT name, url, config FROM data_sources WHERE name='500万彩票'")
source = cursor.fetchone()
if source:
    print(f"✓ 数据源: {source[0]}")
    print(f"  URL: {source[1]}")
    config = json.loads(source[2])
    print(f"  分类: {config.get('category')}")
    print(f"  描述: {config.get('description')}")
    print(f"  自动抓取: {'是' if config.get('auto_crawl') else '否'}")
else:
    print("✗ 数据源不存在")

conn.close()

print("\n" + "="*70)
print("✅ 数据重置完成！")
print("="*70)
print("\n📊 总结:")
print("  ✓ 赛事编号格式：周一001, 周二001... (符合竞彩标准)")
print("  ✓ 数据源：500万彩票网已配置")
print("  ✓ 比赛数据：10场比赛已插入")
print("  ✓ 时间范围：近三天（2026-01-27 至 2026-01-29）")
print("  ✓ 数据完整：包含赔率、热度、联赛等所有字段")
