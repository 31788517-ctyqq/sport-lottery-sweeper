# 体育彩票扫盘系统 - 关键业务视图创建脚本
# 通过SQLAlchemy安全创建业务视图

from sqlalchemy import text, inspect
from backend.database import engine, SessionLocal
from backend.models import Base
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_business_views():
    """创建关键业务视图"""
    
    print("📊 开始创建关键业务视图")
    print("="*50)
    
    # 检查数据库类型
    db_type = "SQLite" if 'sqlite' in str(engine.url) else "PostgreSQL/MySQL"
    print(f"📊 数据库类型: {db_type}")
    
    # 定义关键业务视图
    business_views = [
        {
            'name': 'vw_active_matches_today',
            'sql': '''CREATE VIEW IF NOT EXISTS vw_active_matches_today AS
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
                      ORDER BY m.importance DESC, m.scheduled_kickoff ASC''',
            'desc': '今日活跃比赛视图 - 首页展示核心数据'
        },
        {
            'name': 'vw_user_login_stats', 
            'sql': '''CREATE VIEW IF NOT EXISTS vw_user_login_stats AS
                      SELECT u.id as user_id, u.username, u.email, u.role, u.status,
                             COUNT(ull.id) as total_logins,
                             COUNT(CASE WHEN ull.success = 1 THEN 1 END) as successful_logins,
                             COUNT(CASE WHEN ull.success = 0 THEN 1 END) as failed_logins,
                             MAX(ull.login_at) as last_login,
                             MIN(ull.login_at) as first_login
                      FROM users u
                      LEFT JOIN user_login_logs ull ON u.id = ull.user_id
                      GROUP BY u.id, u.username, u.email, u.role, u.status''',
            'desc': '用户登录统计视图 - 安全分析和用户行为分析'
        },
        {
            'name': 'vw_match_intelligence_summary',
            'sql': '''CREATE VIEW IF NOT EXISTS vw_match_intelligence_summary AS
                      SELECT m.id as match_id, m.match_identifier, m.match_date,
                             l.name as league_name, ht.name as home_team, at.name as away_team,
                             m.importance, m.status,
                             COUNT(mi.id) as intelligence_count,
                             COUNT(CASE WHEN mi.confidence_level >= 0.8 THEN 1 END) as high_confidence_count,
                             AVG(mi.confidence_level) as avg_confidence,
                             STRING_AGG(DISTINCT mi.source_name, ', ') as sources
                      FROM matches m
                      LEFT JOIN leagues l ON m.league_id = l.id
                      LEFT JOIN teams ht ON m.home_team_id = ht.id
                      LEFT JOIN teams at ON m.away_team_id = at.id
                      LEFT JOIN match_intelligence mi ON m.id = mi.match_id
                      WHERE m.is_published = 1
                      GROUP BY m.id, m.match_identifier, m.match_date, l.name, ht.name, at.name, m.importance, m.status''',
            'desc': '比赛情报汇总视图 - 智能分析核心数据'
        },
        {
            'name': 'vw_popular_leagues',
            'sql': '''CREATE VIEW IF NOT EXISTS vw_popular_leagues AS
                      SELECT l.id, l.name, l.short_name, l.country, l.category,
                             COUNT(m.id) as total_matches,
                             COUNT(CASE WHEN m.match_date >= date('now') THEN 1 END) as upcoming_matches,
                             COUNT(CASE WHEN m.status = 'completed' THEN 1 END) as completed_matches,
                             AVG(CASE WHEN m.home_score IS NOT NULL AND m.away_score IS NOT NULL 
                                 THEN CAST(m.home_score AS FLOAT) / (CAST(m.home_score AS FLOAT) + CAST(m.away_score AS FLOAT)) END) as avg_home_win_rate
                      FROM leagues l
                      LEFT JOIN matches m ON l.id = m.league_id
                      WHERE l.is_active = 1
                      GROUP BY l.id, l.name, l.short_name, l.country, l.category
                      HAVING COUNT(m.id) > 0
                      ORDER BY upcoming_matches DESC, total_matches DESC''',
            'desc': '热门联赛排行视图 - 运营决策支持'
        },
        {
            'name': 'vw_user_activity_summary',
            'sql': '''CREATE VIEW IF NOT EXISTS vw_user_activity_summary AS
                      SELECT DATE(u.created_at) as register_date,
                             u.role, u.status,
                             COUNT(u.id) as new_registrations,
                             COUNT(CASE WHEN u.last_login_at >= datetime('now', '-7 days') THEN 1 END) as active_last_7_days,
                             COUNT(CASE WHEN u.last_login_at >= datetime('now', '-30 days') THEN 1 END) as active_last_30_days,
                             COUNT(ull.id) as total_login_attempts,
                             COUNT(CASE WHEN ull.success = 1 THEN 1 END) as successful_logins,
                             ROUND(COUNT(CASE WHEN ull.success = 1 THEN 1 END) * 100.0 / COUNT(ull.id), 2) as login_success_rate
                      FROM users u
                      LEFT JOIN user_login_logs ull ON u.id = ull.user_id
                      WHERE u.created_at >= datetime('now', '-90 days')
                      GROUP BY DATE(u.created_at), u.role, u.status
                      ORDER BY register_date DESC''',
            'desc': '用户活动汇总视图 - 用户行为分析和留存分析'
        },
        {
            'name': 'vw_system_health_metrics',
            'sql': '''CREATE VIEW IF NOT EXISTS vw_system_health_metrics AS
                      SELECT 'Total Users' as metric_category, 'count' as metric_type, 
                             COUNT(*) as metric_value, 'users' as unit
                      FROM users
                      UNION ALL
                      SELECT 'Active Users (7d)' as metric_category, 'count' as metric_type,
                             COUNT(CASE WHEN last_login_at >= datetime('now', '-7 days') THEN 1 END) as metric_value, 'users' as unit
                      FROM users
                      UNION ALL
                      SELECT 'Today Active Matches' as metric_category, 'count' as metric_type,
                             COUNT(*) as metric_value, 'matches' as unit
                      FROM matches WHERE match_date = date('now') AND is_published = 1
                      UNION ALL
                      SELECT 'Failed Logins (24h)' as metric_category, 'count' as metric_type,
                             COUNT(*) as metric_value, 'attempts' as unit
                      FROM user_login_logs 
                      WHERE success = 0 AND login_at >= datetime('now', '-24 hours')
                      UNION ALL
                      SELECT 'High Importance Matches' as metric_category, 'count' as metric_type,
                             COUNT(*) as metric_value, 'matches' as unit
                      FROM matches WHERE importance >= 8 AND match_date >= date('now')
                      UNION ALL
                      SELECT 'Intelligence Coverage Rate' as metric_category, 'percentage' as metric_type,
                             ROUND(COUNT(mi.id) * 100.0 / COUNT(DISTINCT m.id), 2) as metric_value, 'percent' as unit
                      FROM matches m
                      LEFT JOIN match_intelligence mi ON m.id = mi.match_id
                      WHERE m.match_date >= date('now', '-7 days')''',
            'desc': '系统健康指标视图 - 实时监控和运维决策'
        }
    ]
    
    success_count = 0
    
    with SessionLocal() as session:
        print("\n🎯 创建业务视图...")
        
        for i, view in enumerate(business_views, 1):
            try:
                print(f"[{i}/{len(business_views)}] 创建视图: {view['name']}")
                print(f"        用途: {view['desc']}")
                
                # 对于PostgreSQL使用不同的字符串聚合函数
                sql = view['sql']
                if 'STRING_AGG' in sql and db_type != "SQLite":
                    sql = sql.replace('STRING_AGG(DISTINCT mi.source_name, \', \')', 'ARRAY_AGG(DISTINCT mi.source_name)')
                
                session.execute(text(sql))
                session.commit()
                print(f"        ✅ 创建成功")
                success_count += 1
                
            except Exception as e:
                session.rollback()
                if "already exists" in str(e).lower():
                    print(f"        ℹ️  视图已存在")
                    success_count += 1
                else:
                    print(f"        ❌ 创建失败: {str(e)[:100]}")
        
        # 验证视图创建结果
        print("\n🔍 验证视图创建结果...")
        try:
            inspector = inspect(engine)
            views = [obj for obj in inspector.get_table_names() if obj.startswith('vw_')]
            print(f"✅ 发现 {len(views)} 个业务视图:")
            for view in sorted(views):
                print(f"   • {view}")
        except Exception as e:
            print(f"⚠️  视图验证失败: {e}")
    
    print(f"\n🎉 业务视图创建完成! 成功创建/验证 {success_count}/{len(business_views)} 个视图")
    
    # 显示使用示例
    print("\n📋 业务视图使用示例:")
    examples = [
        "SELECT * FROM vw_active_matches_today LIMIT 10;  -- 今日比赛",
        "SELECT * FROM vw_user_login_stats WHERE failed_logins > 0;  -- 异常登录用户", 
        "SELECT * FROM vw_system_health_metrics;  -- 系统健康状态",
        "SELECT * FROM vw_popular_leagues LIMIT 5;  -- 热门联赛排行"
    ]
    
    for example in examples:
        print(f"   {example}")
    
    return success_count == len(business_views)

if __name__ == "__main__":
    create_business_views()