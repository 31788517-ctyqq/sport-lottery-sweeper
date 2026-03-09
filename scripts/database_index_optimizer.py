#!/usr/bin/env python3
"""
数据库索引优化和视图管理工具
功能：
1. 审计现有索引策略
2. 优化索引配置
3. 创建关键业务视图
4. 实施数据清理脚本
"""

import sqlite3
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
import json

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseIndexOptimizer:
    """数据库索引优化器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"成功连接到数据库: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.conn:
            self.conn.close()
            logger.info("数据库连接已关闭")
    
    def audit_indexes(self) -> Dict:
        """审计现有索引"""
        logger.info("开始审计数据库索引...")
        
        cursor = self.conn.cursor()
        
        # 获取所有表的索引信息
        cursor.execute("""
            SELECT 
                tbl_name as table_name,
                sql
            FROM sqlite_master 
            WHERE type = 'index' AND tbl_name NOT LIKE 'sqlite_%'
            ORDER BY tbl_name
        """)
        
        indexes = cursor.fetchall()
        
        # 获取表的基本信息
        cursor.execute("""
            SELECT 
                name as table_name,
                sql as create_statement
            FROM sqlite_master 
            WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
        """)
        
        tables = cursor.fetchall()
        
        # 分析索引使用情况
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1")
        sample_table = cursor.fetchone()
        
        analysis = {
            'total_tables': len(tables),
            'total_indexes': len(indexes),
            'tables': [],
            'indexes_by_table': {},
            'recommendations': []
        }
        
        # 分析每个表的索引
        for table in tables:
            table_name = table['table_name']
            table_indexes = [idx for idx in indexes if idx['table_name'] == table_name]
            
            # 获取表的行数
            try:
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
                row_count = cursor.fetchone()['count']
            except:
                row_count = 0
            
            table_info = {
                'name': table_name,
                'row_count': row_count,
                'index_count': len(table_indexes),
                'indexes': []
            }
            
            for idx in table_indexes:
                # 从CREATE INDEX语句中提取索引信息
                idx_sql = idx['sql']
                if idx_sql:
                    # 提取索引名称和列
                    import re
                    match = re.search(r'CREATE (?:UNIQUE )?INDEX ([\w]+) ON ([\w]+)\(([^)]+)\)', idx_sql)
                    if match:
                        index_info = {
                            'name': match.group(1),
                            'table': match.group(2),
                            'columns': [col.strip() for col in match.group(3).split(',')],
                            'unique': 'UNIQUE' in idx_sql.upper(),
                            'sql': idx_sql
                        }
                        table_info['indexes'].append(index_info)
            
            analysis['tables'].append(table_info)
            analysis['indexes_by_table'][table_name] = table_info['indexes']
        
        # 生成优化建议
        analysis['recommendations'] = self._generate_index_recommendations(analysis)
        
        return analysis
    
    def _generate_index_recommendations(self, analysis: Dict) -> List[Dict]:
        """生成索引优化建议"""
        recommendations = []
        
        # 分析高频查询场景的索引需求
        common_query_patterns = [
            {
                'scenario': '用户登录查询',
                'tables': ['users'],
                'suggested_indexes': [
                    {'columns': ['username'], 'unique': True, 'reason': '用户名登录查询'},
                    {'columns': ['email'], 'unique': True, 'reason': '邮箱登录查询'},
                    {'columns': ['status', 'role'], 'unique': False, 'reason': '按状态和角色筛选用户'}
                ]
            },
            {
                'scenario': '比赛列表查询',
                'tables': ['matches'],
                'suggested_indexes': [
                    {'columns': ['match_date', 'status'], 'unique': False, 'reason': '按日期和状态查询比赛'},
                    {'columns': ['league_id', 'match_date'], 'unique': False, 'reason': '按联赛和日期查询比赛'},
                    {'columns': ['home_team_id', 'away_team_id', 'match_date'], 'unique': False, 'reason': '按主客队和日期查询比赛'},
                    {'columns': ['status', 'match_date', 'priority'], 'unique': False, 'reason': '按状态、日期和优先级排序'}
                ]
            },
            {
                'scenario': '联赛查询',
                'tables': ['leagues'],
                'suggested_indexes': [
                    {'columns': ['country', 'is_active'], 'unique': False, 'reason': '按国家和活跃状态查询联赛'},
                    {'columns': ['is_popular', 'is_active'], 'unique': False, 'reason': '查询热门活跃联赛'},
                    {'columns': ['level', 'type'], 'unique': False, 'reason': '按级别和类型查询联赛'}
                ]
            },
            {
                'scenario': '用户活动分析',
                'tables': ['user_activities'],
                'suggested_indexes': [
                    {'columns': ['user_id', 'activity_time'], 'unique': False, 'reason': '按用户和时间查询活动'},
                    {'columns': ['activity_type', 'activity_time'], 'unique': False, 'reason': '按活动类型和时间查询'},
                    {'columns': ['resource_type', 'resource_id'], 'unique': False, 'reason': '按资源类型和ID查询活动'}
                ]
            },
            {
                'scenario': '登录日志分析',
                'tables': ['user_login_logs'],
                'suggested_indexes': [
                    {'columns': ['user_id', 'login_at'], 'unique': False, 'reason': '按用户和时间查询登录记录'},
                    {'columns': ['login_ip', 'login_at'], 'unique': False, 'reason': '按IP和时间查询登录记录'},
                    {'columns': ['success', 'login_at'], 'unique': False, 'reason': '按成功状态和时间查询登录记录'}
                ]
            }
        ]
        
        for pattern in common_query_patterns:
            for table_name in pattern['tables']:
                existing_indexes = set()
                for idx in analysis['indexes_by_table'].get(table_name, []):
                    existing_indexes.add(tuple(sorted(idx['columns'])))
                
                for suggested_idx in pattern['suggested_indexes']:
                    key = tuple(sorted(suggested_idx['columns']))
                    if key not in existing_indexes:
                        recommendations.append({
                            'priority': 'HIGH' if 'login' in pattern['scenario'].lower() or 'user' in pattern['scenario'].lower() else 'MEDIUM',
                            'table': table_name,
                            'scenario': pattern['scenario'],
                            'columns': suggested_idx['columns'],
                            'unique': suggested_idx.get('unique', False),
                            'reason': suggested_idx['reason'],
                            'sql': self._build_create_index_sql(table_name, suggested_idx)
                        })
        
        return recommendations
    
    def _build_create_index_sql(self, table: str, index_info: Dict) -> str:
        """构建创建索引的SQL语句"""
        columns = ', '.join(index_info['columns'])
        unique_part = 'UNIQUE ' if index_info.get('unique', False) else ''
        index_name = f"idx_{table}_{'_'.join(index_info['columns'])}"
        
        return f"CREATE {unique_part}INDEX {index_name} ON {table}({columns});"
    
    def optimize_indexes(self, apply_changes: bool = False) -> Dict:
        """优化索引配置"""
        logger.info("开始优化索引配置...")
        
        audit_result = self.audit_indexes()
        optimizations = []
        
        for rec in audit_result['recommendations']:
            if rec['priority'] == 'HIGH':
                optimization = {
                    'table': rec['table'],
                    'sql': rec['sql'],
                    'reason': rec['reason'],
                    'applied': False
                }
                
                if apply_changes:
                    try:
                        cursor = self.conn.cursor()
                        cursor.execute(rec['sql'])
                        self.conn.commit()
                        optimization['applied'] = True
                        logger.info(f"已创建索引: {rec['sql']}")
                    except Exception as e:
                        logger.error(f"创建索引失败: {e}")
                        optimization['error'] = str(e)
                
                optimizations.append(optimization)
        
        return {
            'audit': audit_result,
            'optimizations': optimizations,
            'summary': {
                'total_recommendations': len(audit_result['recommendations']),
                'high_priority': len([r for r in audit_result['recommendations'] if r['priority'] == 'HIGH']),
                'optimizations_applied': len([o for o in optimizations if o.get('applied', False)])
            }
        }

class BusinessViewCreator:
    """业务视图创建器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"成功连接到数据库: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.conn:
            self.conn.close()
    
    def create_key_views(self) -> Dict:
        """创建关键业务视图"""
        logger.info("开始创建关键业务视图...")
        
        views_sql = {
            'vw_active_matches_today': """
                CREATE VIEW IF NOT EXISTS vw_active_matches_today AS
                SELECT 
                    m.id,
                    m.match_identifier,
                    m.match_date,
                    m.scheduled_kickoff,
                    m.status,
                    m.importance,
                    l.name as league_name,
                    l.code as league_code,
                    ht.name as home_team_name,
                    at.name as away_team_name,
                    m.home_score,
                    m.away_score,
                    m.is_featured,
                    m.popularity
                FROM matches m
                LEFT JOIN leagues l ON m.league_id = l.id
                LEFT JOIN teams ht ON m.home_team_id = ht.id
                LEFT JOIN teams at ON m.away_team_id = at.id
                WHERE m.match_date = date('now')
                AND m.is_published = 1
                ORDER BY m.importance DESC, m.scheduled_kickoff ASC;
            """,
            
            'vw_user_login_stats': """
                CREATE VIEW IF NOT EXISTS vw_user_login_stats AS
                SELECT 
                    u.id as user_id,
                    u.username,
                    u.email,
                    u.role,
                    u.status,
                    COUNT(ull.id) as total_logins,
                    COUNT(CASE WHEN ull.success = 1 THEN 1 END) as successful_logins,
                    COUNT(CASE WHEN ull.success = 0 THEN 1 END) as failed_logins,
                    MAX(ull.login_at) as last_login,
                    MIN(ull.login_at) as first_login,
                    COUNT(DISTINCT DATE(ull.login_at)) as active_days
                FROM users u
                LEFT JOIN user_login_logs ull ON u.id = ull.user_id
                GROUP BY u.id, u.username, u.email, u.role, u.status;
            """,
            
            'vw_match_intelligence_summary': """
                CREATE VIEW IF NOT EXISTS vw_match_intelligence_summary AS
                SELECT 
                    m.id as match_id,
                    m.match_identifier,
                    m.match_date,
                    m.status,
                    l.name as league_name,
                    ht.name as home_team_name,
                    at.name as away_team_name,
                    COUNT(i.id) as total_intelligence_items,
                    COUNT(CASE WHEN i.confidence_level >= 0.8 THEN 1 END) as high_confidence_items,
                    COUNT(CASE WHEN i.category = 'injury' THEN 1 END) as injury_items,
                    COUNT(CASE WHEN i.category = 'transfer' THEN 1 END) as transfer_items,
                    COUNT(CASE WHEN i.category = 'weather' THEN 1 END) as weather_items,
                    MAX(i.created_at) as latest_intelligence
                FROM matches m
                LEFT JOIN leagues l ON m.league_id = l.id
                LEFT JOIN teams ht ON m.home_team_id = ht.id
                LEFT JOIN teams at ON m.away_team_id = at.id
                LEFT JOIN intelligence i ON m.id = i.match_id
                WHERE m.is_published = 1
                GROUP BY m.id, m.match_identifier, m.match_date, m.status, l.name, ht.name, at.name;
            """,
            
            'vw_popular_leagues': """
                CREATE VIEW IF NOT EXISTS vw_popular_leagues AS
                SELECT 
                    l.id,
                    l.name,
                    l.code,
                    l.country,
                    l.level,
                    l.total_matches,
                    l.total_views,
                    l.total_followers,
                    l.is_popular,
                    COUNT(m.id) as upcoming_matches,
                    AVG(CASE WHEN m.home_score IS NOT NULL AND m.away_score IS NOT NULL 
                        THEN CAST(m.home_score AS FLOAT) / (m.home_score + m.away_score + 0.001) 
                        ELSE NULL END) as avg_home_win_rate
                FROM leagues l
                LEFT JOIN matches m ON l.id = m.league_id 
                    AND m.match_date >= date('now')
                    AND m.status = 'scheduled'
                WHERE l.is_active = 1
                GROUP BY l.id, l.name, l.code, l.country, l.level, l.total_matches, 
                         l.total_views, l.total_followers, l.is_popular
                ORDER BY l.is_popular DESC, l.level ASC, l.total_views DESC;
            """,
            
            'vw_user_activity_summary': """
                CREATE VIEW IF NOT EXISTS vw_user_activity_summary AS
                SELECT 
                    ua.user_id,
                    u.username,
                    u.role,
                    COUNT(ua.id) as total_activities,
                    COUNT(DISTINCT DATE(ua.activity_time)) as active_days,
                    COUNT(DISTINCT ua.resource_type) as accessed_resources,
                    MAX(ua.activity_time) as last_activity,
                    COUNT(CASE WHEN ua.http_status >= 400 THEN 1 END) as error_count
                FROM user_activities ua
                JOIN users u ON ua.user_id = u.id
                WHERE ua.activity_time >= datetime('now', '-30 days')
                GROUP BY ua.user_id, u.username, u.role
                ORDER BY total_activities DESC;
            """,
            
            'vw_system_health_metrics': """
                CREATE VIEW IF NOT EXISTS vw_system_health_metrics AS
                SELECT 
                    'Database Size' as metric_name,
                    ROUND(CAST(page_count * page_size AS FLOAT) / 1024 / 1024, 2) as metric_value,
                    'MB' as unit,
                    datetime('now') as measured_at
                FROM pragma_page_count(), pragma_page_size()
                UNION ALL
                SELECT 
                    'Total Users' as metric_name,
                    COUNT(*) as metric_value,
                    'count' as unit,
                    datetime('now') as measured_at
                FROM users
                UNION ALL
                SELECT 
                    'Active Matches Today' as metric_name,
                    COUNT(*) as metric_value,
                    'count' as unit,
                    datetime('now') as measured_at
                FROM matches 
                WHERE match_date = date('now') AND is_published = 1
                UNION ALL
                SELECT 
                    'Failed Login Attempts (24h)' as metric_name,
                    COUNT(*) as metric_value,
                    'count' as unit,
                    datetime('now') as measured_at
                FROM user_login_logs 
                WHERE success = 0 AND login_at >= datetime('now', '-24 hours');
            """
        }
        
        results = {'created_views': [], 'failed_views': []}
        
        for view_name, view_sql in views_sql.items():
            try:
                cursor = self.conn.cursor()
                cursor.execute(view_sql)
                self.conn.commit()
                results['created_views'].append(view_name)
                logger.info(f"成功创建视图: {view_name}")
            except Exception as e:
                results['failed_views'].append({'view': view_name, 'error': str(e)})
                logger.error(f"创建视图失败 {view_name}: {e}")
        
        return results

class DataCleanupManager:
    """数据清理管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"成功连接到数据库: {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"数据库连接失败: {e}")
            return False
    
    def disconnect(self):
        """断开数据库连接"""
        if self.conn:
            self.conn.close()
    
    def cleanup_old_data(self, dry_run: bool = True) -> Dict:
        """清理旧数据"""
        logger.info(f"开始数据清理{'[演练模式]' if dry_run else ''}...")
        
        cleanup_results = {
            'cleaned_records': {},
            'freed_space_mb': 0,
            'operations': []
        }
        
        cursor = self.conn.cursor()
        
        # 定义清理规则
        cleanup_rules = [
            {
                'table': 'user_login_logs',
                'condition': "login_at < datetime('now', '-90 days')",
                'description': '清理90天前的登录日志',
                'retention_days': 90
            },
            {
                'table': 'user_activities',
                'condition': "activity_time < datetime('now', '-180 days')",
                'description': '清理180天前的用户活动记录',
                'retention_days': 180
            },
            {
                'table': 'user_login_logs',
                'condition': "success = 0 AND login_at < datetime('now', '-30 days')",
                'description': '清理30天前的失败登录尝试',
                'retention_days': 30
            },
            {
                'table': 'crawler_logs',
                'condition': "created_at < datetime('now', '-60 days')",
                'description': '清理60天前的爬虫日志',
                'retention_days': 60
            }
        ]
        
        for rule in cleanup_rules:
            try:
                # 先统计要删除的记录数
                count_sql = f"SELECT COUNT(*) as count FROM {rule['table']} WHERE {rule['condition']}"
                cursor.execute(count_sql)
                count_result = cursor.fetchone()
                record_count = count_result['count'] if count_result else 0
                
                cleanup_results['cleaned_records'][rule['table']] = {
                    'condition': rule['condition'],
                    'count': record_count,
                    'description': rule['description']
                }
                
                # 如果不是演练模式，执行删除
                if not dry_run and record_count > 0:
                    delete_sql = f"DELETE FROM {rule['table']} WHERE {rule['condition']}"
                    cursor.execute(delete_sql)
                    self.conn.commit()
                    cleanup_results['operations'].append({
                        'table': rule['table'],
                        'action': 'deleted',
                        'count': record_count,
                        'sql': delete_sql
                    })
                    logger.info(f"已清理 {record_count} 条 {rule['table']} 记录")
                else:
                    cleanup_results['operations'].append({
                        'table': rule['table'],
                        'action': 'would_delete' if not dry_run else 'counted',
                        'count': record_count,
                        'sql': f"DELETE FROM {rule['table']} WHERE {rule['condition']}"
                    })
                    
            except Exception as e:
                logger.error(f"清理 {rule['table']} 失败: {e}")
                cleanup_results['operations'].append({
                    'table': rule['table'],
                    'action': 'failed',
                    'error': str(e)
                })
        
        return cleanup_results
    
    def optimize_database(self) -> Dict:
        """优化数据库性能"""
        logger.info("开始数据库优化...")
        
        cursor = self.conn.cursor()
        optimization_results = {'operations': []}
        
        try:
            # 执行VACUUM命令回收空间
            cursor.execute("VACUUM")
            self.conn.commit()
            optimization_results['operations'].append({
                'operation': 'VACUUM',
                'status': 'success',
                'description': '回收数据库空间并重建索引'
            })
            logger.info("VACUUM操作完成")
            
            # 更新统计信息
            cursor.execute("ANALYZE")
            self.conn.commit()
            optimization_results['operations'].append({
                'operation': 'ANALYZE',
                'status': 'success',
                'description': '更新查询优化器统计信息'
            })
            logger.info("ANALYZE操作完成")
            
        except Exception as e:
            logger.error(f"数据库优化失败: {e}")
            optimization_results['operations'].append({
                'operation': 'OPTIMIZE',
                'status': 'failed',
                'error': str(e)
            })
        
        return optimization_results

def main():
    """主函数"""
    BASE_DIR = Path(__file__).resolve().parent.parent
    db_path = BASE_DIR / "data/sport_lottery.db"
    
    logger.info("=== 数据库索引优化和视图管理工具 ===")
    
    # 1. 索引优化
    optimizer = DatabaseIndexOptimizer(db_path)
    if optimizer.connect():
        # 审计索引
        audit_result = optimizer.audit_indexes()
        logger.info(f"审计完成: {audit_result['total_tables']} 个表, {audit_result['total_indexes']} 个索引")
        
        # 优化索引（演练模式）
        optimization_result = optimizer.optimize_indexes(apply_changes=False)
        logger.info(f"索引优化建议: {optimization_result['summary']['total_recommendations']} 条")
        
        # 打印高优先级建议
        high_priority = [r for r in optimization_result['audit']['recommendations'] if r['priority'] == 'HIGH']
        if high_priority:
            logger.info("高优先级索引建议:")
            for rec in high_priority[:5]:  # 只显示前5条
                logger.info(f"  - {rec['scenario']}: {rec['sql']}")
        
        optimizer.disconnect()
    
    # 2. 创建业务视图
    view_creator = BusinessViewCreator(db_path)
    if view_creator.connect():
        views_result = view_creator.create_key_views()
        logger.info(f"视图创建完成: {len(views_result['created_views'])} 个成功, {len(views_result['failed_views'])} 个失败")
        view_creator.disconnect()
    
    # 3. 数据清理（演练模式）
    cleanup_manager = DataCleanupManager(db_path)
    if cleanup_manager.connect():
        cleanup_result = cleanup_manager.cleanup_old_data(dry_run=True)
        total_records = sum(info['count'] for info in cleanup_result['cleaned_records'].values())
        logger.info(f"数据清理演练: 可清理 {total_records} 条记录")
        cleanup_manager.disconnect()
    
    logger.info("=== 数据库优化完成 ===")

if __name__ == "__main__":
    main()