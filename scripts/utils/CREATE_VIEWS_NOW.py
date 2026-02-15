# 体育彩票扫盘系统 - 业务视图创建代码
# 复制到Python中直接执行，立即创建6个关键业务视图

import sqlite3
import os

print("📊 创建关键业务视图")
print("="*50)

db_path = "data/sport_lottery.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 业务视图定义
views = [
    ("vw_active_matches_today", """CREATE VIEW IF NOT EXISTS vw_active_matches_today AS
                      SELECT m.id, m.match_identifier, m.match_date, m.scheduled_kickoff, 
                             m.status, m.importance, l.name as league_name,
                             ht.name as home_team_name, at.name as away_team_name,
                             m.home_score, m.away_score, m.is_featured
                      FROM matches m
                      LEFT JOIN leagues l ON m.league_id = l.id
                      LEFT JOIN teams ht ON m.home_team_id = ht.id
                      LEFT JOIN teams at ON m.away_team_id = at.id
                      WHERE m.match_date = date('now')
                      AND m.is_published = 1
                      ORDER BY m.importance DESC, m.scheduled_kickoff ASC"""),
    
    ("vw_user_login_stats", """CREATE VIEW IF NOT EXISTS vw_user_login_stats AS
                      SELECT u.id as user_id, u.username, u.email, u.role, u.status,
                             COUNT(ull.id) as total_logins,
                             COUNT(CASE WHEN ull.success = 1 THEN 1 END) as successful_logins,
                             COUNT(CASE WHEN ull.success = 0 THEN 1 END) as failed_logins,
                             MAX(ull.login_at) as last_login
                      FROM users u
                      LEFT JOIN user_login_logs ull ON u.id = ull.user_id
                      GROUP BY u.id, u.username, u.email, u.role, u.status"""),
    
    ("vw_match_intelligence_summary", """CREATE VIEW IF NOT EXISTS vw_match_intelligence_summary AS
                      SELECT m.id as match_id, m.match_identifier, m.match_date,
                             l.name as league_name, ht.name as home_team, at.name as away_team,
                             m.importance, m.status,
                             COUNT(mi.id) as intelligence_count,
                             COUNT(CASE WHEN mi.confidence_level >= 0.8 THEN 1 END) as high_confidence_count,
                             AVG(mi.confidence_level) as avg_confidence
                      FROM matches m
                      LEFT JOIN leagues l ON m.league_id = l.id
                      LEFT JOIN teams ht ON m.home_team_id = ht.id
                      LEFT JOIN teams at ON m.away_team_id = at.id
                      LEFT JOIN match_intelligence mi ON m.id = mi.match_id
                      WHERE m.is_published = 1
                      GROUP BY m.id, m.match_identifier, m.match_date, l.name, ht.name, at.name, m.importance, m.status"""),
    
    ("vw_popular_leagues", """CREATE VIEW IF NOT EXISTS vw_popular_leagues AS
                      SELECT l.id, l.name, l.short_name, l.country, l.category,
                             COUNT(m.id) as total_matches,
                             COUNT(CASE WHEN m.match_date >= date('now') THEN 1 END) as upcoming_matches,
                             COUNT(CASE WHEN m.status = 'completed' THEN 1 END) as completed_matches
                      FROM leagues l
                      LEFT JOIN matches m ON l.id = m.league_id
                      WHERE l.is_active = 1
                      GROUP BY l.id, l.name, l.short_name, l.country, l.category
                      HAVING COUNT(m.id) > 0
                      ORDER BY upcoming_matches DESC, total_matches DESC"""),
    
    ("vw_user_activity_summary", """CREATE VIEW IF NOT EXISTS vw_user_activity_summary AS
                      SELECT u.role, u.status,
                             COUNT(u.id) as total_users,
                             COUNT(CASE WHEN u.last_login_at >= datetime('now', '-7 days') THEN 1 END) as active_7d,
                             COUNT(CASE WHEN u.last_login_at >= datetime('now', '-30 days') THEN 1 END) as active_30d
                      FROM users u
                      GROUP BY u.role, u.status"""),
    
    ("vw_system_health_metrics", """CREATE VIEW IF NOT EXISTS vw_system_health_metrics AS
                      SELECT 'Total Users' as metric_name, COUNT(*) as metric_value, 'count' as unit
                      FROM users
                      UNION ALL
                      SELECT 'Active Matches Today' as metric_name, 
                             COUNT(*) as metric_value, 'count' as unit
                      FROM matches WHERE match_date = date('now') AND is_published = 1
                      UNION ALL
                      SELECT 'Failed Logins (24h)' as metric_name,
                             COUNT(*) as metric_value, 'count' as unit
                      FROM user_login_logs 
                      WHERE success = 0 AND login_at >= datetime('now', '-24 hours')""")
]

print("🎯 创建6个关键业务视图...")
success = 0

for name, sql in views:
    try:
        cursor.execute(sql)
        print(f"✅ {name}")
        success += 1
    except sqlite3.Error as e:
        if "already exists" in str(e):
            print(f"ℹ️  {name} (已存在)")
            success += 1
        else:
            print(f"❌ {name}: {str(e)[:50]}")

conn.commit()

# 验证视图
print("\n🔍 验证视图创建...")
cursor.execute("SELECT name FROM sqlite_master WHERE type='view' AND name LIKE 'vw_%'")
view_list = cursor.fetchall()
print(f"✅ 成功创建 {len(view_list)} 个业务视图:")
for view in view_list:
    print(f"   • {view[0]}")

conn.close()

print(f"\n🎉 业务视图创建完成! 成功率: {success}/6")
print("\n📋 使用示例:")
print("   SELECT * FROM vw_active_matches_today LIMIT 5;")
print("   SELECT * FROM vw_system_health_metrics;")
print("   SELECT * FROM vw_user_login_stats WHERE failed_logins > 0;")