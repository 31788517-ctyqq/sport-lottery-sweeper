# 创建完整的比赛数据（包含前端所需的所有字段）
import sqlite3
import json
from datetime import datetime

print("正在创建完整的500万彩票数据和比赛数据...")

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
SELECT id FROM data_sources WHERE name = '500万彩票'
""")
if not cursor.fetchone():
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
else:
    print("✓ 数据源已存在")

# 2. 创建完整的比赛数据（包含所有前端字段）
matches = [
    ("M001", "北京国安", "上海申花", "2026-01-27 19:35:00", "中超", "未开始", 2.15, 3.20, 2.85, 8500),
    ("M002", "山东泰山", "广州恒大", "2026-01-27 20:00:00", "中超", "未开始", 1.95, 3.40, 3.10, 9200),
    ("M003", "江苏苏宁", "河南建业", "2026-01-28 15:30:00", "中超", "未开始", 2.40, 3.15, 2.60, 6800),
    ("M004", "天津泰达", "重庆当代", "2026-01-28 19:35:00", "中超", "未开始", 2.80, 3.05, 2.35, 5400),
    ("M005", "武汉卓尔", "石家庄永昌", "2026-01-29 19:35:00", "中超", "未开始", 2.10, 3.25, 2.90, 7200),
    ("M006", "曼联", "利物浦", "2026-01-27 22:00:00", "英超", "未开始", 2.60, 3.30, 2.45, 15600),
    ("M007", "切尔西", "阿森纳", "2026-01-28 00:30:00", "英超", "未开始", 2.35, 3.45, 2.55, 18900),
    ("M008", "皇马", "巴萨", "2026-01-28 03:00:00", "西甲", "未开始", 2.20, 3.60, 2.70, 24300),
    ("M009", "拜仁", "多特", "2026-01-29 04:00:00", "德甲", "未开始", 1.85, 3.75, 3.20, 16700),
    ("M010", "大阪钢巴", "浦和红钻", "2026-01-27 18:00:00", "日职联", "未开始", 2.65, 3.10, 2.40, 4300),
]

inserted = 0
for match in matches:
    cursor.execute("SELECT id FROM football_matches WHERE match_id = ?", (match[0],))
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO football_matches 
        (match_id, home_team, away_team, match_time, league, status, 
         odds_home_win, odds_draw, odds_away_win, popularity, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (match[0], match[1], match[2], match[3], match[4], match[5],
               match[6], match[7], match[8], match[9],
               datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        inserted += 1

conn.commit()
print(f"✓ 成功插入 {inserted} 条完整比赛数据")

# 3. 验证数据
cursor.execute("SELECT COUNT(*) FROM football_matches")
count = cursor.fetchone()[0]
print(f"\n✓ 数据库中共有 {count} 场比赛")

if count > 0:
    print("\n比赛列表（含赔率和热度）：")
    print("ID      主队        客队        时间              联赛    胜   平   负   热度")
    print("-" * 85)
    cursor.execute("""
    SELECT match_id, home_team, away_team, match_time, league, 
           odds_home_win, odds_draw, odds_away_win, popularity 
    FROM football_matches ORDER BY match_time
    """)
    for row in cursor.fetchall():
        print(f"{row[0]}  {row[1]:<10} {row[2]:<10} {row[3]}  {row[4]:<6} {row[5]:.2f} {row[6]:.2f} {row[7]:.2f} {row[8]}")

conn.close()
print("\n✅ 完成！现在刷新页面就能看到完整数据了")
