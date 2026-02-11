import sqlite3
import os

def check_database_completeness(db_path, db_name):
    """检查数据库的模块完整性"""
    if not os.path.exists(db_path):
        print(f"{db_name}: 文件不存在")
        return {}
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表名
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        # 按模块分类统计
        modules = {
            'admin': ['admin_users', 'departments', 'roles', 'permissions'],
            'matches': ['football_matches', 'matches', 'teams', 'leagues', 'venues'],
            'caipiao': ['caipiao_data', 'sp_records', 'draw_prediction_results'],
            'crawler': ['data_sources', 'crawler_configs', 'ip_pools', 'request_headers'],
            'logs': ['log_entries', 'admin_operation_logs', 'admin_login_logs', 'user_activities'],
            'intelligence': ['intelligence', 'intelligence_types', 'intelligence_sources'],
            'hedging': ['hedging_opportunities', 'hedging_configs'],
            'users': ['users', 'user_role_mappings', 'social_accounts']
        }
        
        module_stats = {}
        total_tables = len(tables)
        
        for module_name, module_tables in modules.items():
            existing_tables = [table for table in module_tables if table in tables]
            module_stats[module_name] = {
                'total_expected': len(module_tables),
                'existing': len(existing_tables),
                'completeness': len(existing_tables) / len(module_tables) * 100 if module_tables else 0,
                'tables': existing_tables
            }
            
            # 统计数据量
            data_count = 0
            for table in existing_tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    data_count += count
                except:
                    pass
            module_stats[module_name]['data_count'] = data_count
        
        conn.close()
        
        # 计算整体通过率
        total_expected = sum(len(tables) for tables in modules.values())
        total_existing = sum(stats['existing'] for stats in module_stats.values())
        overall_completeness = total_existing / total_expected * 100 if total_expected > 0 else 0
        
        return {
            'db_name': db_name,
            'db_path': db_path,
            'overall_completeness': overall_completeness,
            'total_tables': total_tables,
            'module_stats': module_stats
        }
        
    except Exception as e:
        print(f"{db_name}: 错误 - {e}")
        return {}

def analyze_all_databases():
    """分析所有数据库文件"""
    databases = [
        ("根目录数据库", "sport_lottery.db"),
        ("Backend数据库", "backend/sport_lottery.db"),
        ("Data数据库", "data/sport_lottery.db"),
        ("Samples数据库", "data/samples/sport_lottery.db"),
        ("Scripts数据库", "scripts/sport_lottery.db"),
        ("Tests数据库", "tests/sport_lottery.db")
    ]
    
    results = []
    for db_name, db_path in databases:
        result = check_database_completeness(db_path, db_name)
        if result:
            results.append(result)
    
    # 按整体完整性排序
    results.sort(key=lambda x: x['overall_completeness'], reverse=True)
    
    print("=== 数据库模块完整性分析 ===\n")
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['db_name']}")
        print(f"   路径: {result['db_path']}")
        print(f"   整体完整性: {result['overall_completeness']:.1f}%")
        print(f"   总表数: {result['total_tables']}")
        print("   模块详情:")
        
        # 按完整性排序显示模块
        sorted_modules = sorted(result['module_stats'].items(), 
                              key=lambda x: x[1]['completeness'], reverse=True)
        
        for module_name, stats in sorted_modules:
            if stats['completeness'] > 0:
                print(f"     - {module_name}: {stats['completeness']:.1f}% "
                      f"({stats['existing']}/{stats['total_expected']} 表, "
                      f"{stats['data_count']} 条数据)")
        
        print()
    
    if results:
        best_db = results[0]
        print(f"🏆 推荐使用: {best_db['db_name']} (完整性: {best_db['overall_completeness']:.1f}%)")
    
    return results

if __name__ == "__main__":
    analyze_all_databases()