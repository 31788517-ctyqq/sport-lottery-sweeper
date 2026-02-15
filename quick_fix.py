# 直接在Python中运行这个脚本来创建数据和检查
import sqlite3
import json
from datetime import datetime

print("正在创建500万彩票数据源...")

# 连接数据库
db_path = 'data/sport_lottery.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. 创建数据源
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

print(f"✓ 数据源创建成功! ID: {cursor.lastrowid}")

# 2. 创建比赛数据
matches = [
    ("M001", "北京国安", "上海申花", "2026-01-27 19:35:00", "中超", "未开始"),
    ("M002", "山东泰山", "广州恒大", "2026-01-27 20:00:00", "中超", "未开始"),
    ("M003", "江苏苏宁", "河南建业", "2026-01-28 15:30:00", "中超", "未开始"),
    ("M004", "天津泰达", "重庆当代", "2026-01-28 19:35:00", "中超", "未开始"),
    ("M005", "武汉卓尔", "石家庄永昌", "2026-01-29 19:35:00", "中超", "未开始"),
    ("M006", "曼联", "利物浦", "2026-01-27 22:00:00", "英超", "未开始"),
    ("M007", "切尔西", "阿森纳", "2026-01-28 00:30:00", "英超", "未开始"),
    ("M008", "皇马", "巴萨", "2026-01-28 03:00:00", "西甲", "未开始"),
    ("M009", "拜仁", "多特", "2026-01-29 04:00:00", "德甲", "未开始"),
    ("M010", "大阪钢巴", "浦和红钻", "2026-01-27 18:00:00", "日职联", "未开始"),
]

inserted = 0
for match in matches:
    cursor.execute("SELECT id FROM football_matches WHERE match_id = ?", (match[0],))
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO football_matches (match_id, home_team, away_team, match_time, league, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (match[0], match[1], match[2], match[3], match[4], match[5],
               datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        inserted += 1

conn.commit()
print(f"✓ 成功插入 {inserted} 条比赛数据")

# 3. 验证数据
cursor.execute("SELECT COUNT(*) FROM football_matches")
count = cursor.fetchone()[0]
print(f"\n✓ 数据库中共有 {count} 场比赛")

if count > 0:
    print("\n比赛列表：")
    print("ID      主队        客队        时间              联赛")
    print("-" * 70)
    cursor.execute("SELECT match_id, home_team, away_team, match_time, league FROM football_matches ORDER BY match_time")
    for row in cursor.fetchall():
        print(f"{row[0]}  {row[1]:<10} {row[2]:<10} {row[3]}  {row[4]}")

conn.close()
print("\n✅ 完成！现在刷新页面就能看到数据了")
