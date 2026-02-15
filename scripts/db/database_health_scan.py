# 体育彩票扫盘系统 - 数据库全面健康扫描
# 深度分析所有表的记录数、索引、性能和优化建议

import sqlite3
import os
from datetime import datetime

def scan_database_health():
    print("🔍 数据库全面健康扫描")
    print("="*60)
    
    db_path = "data/sport_lottery.db"
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 基础信息
    size_mb = os.path.getsize(db_path) / (1024*1024)
    print(f"📊 数据库大小: {size_mb:.2f} MB")
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    all_tables = [row[0] for row in cursor.fetchall()]
    print(f"📋 总表数: {len(all_tables)}")
    
    # 排除系统表
    user_tables = [t for t in all_tables if not t.startswith('sqlite_')]
    print(f"👤 用户表数: {len(user_tables)}")
    
    print("\n" + "="*60)
    print("📈 表记录数分析 (Top 20大表)")
    print("="*60)
    
    table_stats = []
    for table in user_tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            table_stats.append((table, count))
        except Exception as e:
            table_stats.append((table, f"ERROR: {e}"))
    
    # 按记录数排序
    table_stats.sort(key=lambda x: x[1] if isinstance(x[1], int) else 0, reverse=True)
    
    print(f"{'表名':<25} {'记录数':>12} {'状态':>10}")
    print("-"*60)
    
    large_tables = []
    for table, count in table_stats[:20]:
        if isinstance(count, int):
            if count > 100000:
                status = "🔴 超大"
                large_tables.append(table)
            elif count > 10000:
                status = "🟡 大表"
            elif count > 1000:
                status = "🟢 中表"
            else:
                status = "⚪ 小表"
            print(f"{table:<25} {count:>12,} {status:>10}")
        else:
            print(f"{table:<25} {'ERROR':>12} ❌ 异常")
    
    print("\n" + "="*60)
    print("🎯 索引分析")
    print("="*60)
    
    # 获取所有索引
    cursor.execute("SELECT name, tbl_name FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%' ORDER BY tbl_name, name")
    indexes = cursor.fetchall()
    
    # 按表分组索引
    index_by_table = {}
    for idx_name, tbl_name in indexes:
        if tbl_name not in index_by_table:
            index_by_table[tbl_name] = []
        index_by_table[tbl_name].append(idx_name)
    
    print(f"📊 总索引数: {len(indexes)}")
    print(f"📋 有索引的表: {len(index_by_table)}")
    
    # 检查大表是否有足够索引
    print("\n🔍 大表索引检查:")
    for table in large_tables:
        if table in index_by_table:
            idx_count = len(index_by_table[table])
            print(f"   • {table:<20} {idx_count:>2} 个索引 {'✅ 充足' if idx_count >= 3 else '⚠️  可能不足'}")
        else:
            print(f"   • {table:<20} {0:>2} 个索引 ❌ 无索引!")
    
    print("\n" + "="*60)
    print("⚠️  潜在问题识别")
    print("="*60)
    
    issues = []
    
    # 检查无索引的大表
    for table, count in table_stats:
        if isinstance(count, int) and count > 10000:
            if table not in index_by_table or len(index_by_table[table]) < 2:
                issues.append(f"大表 {table}({count:,}条) 缺少索引")
    
    # 检查可能的重复索引
    index_names = [idx[0] for idx in indexes]
    if len(index_names) != len(set(index_names)):
        issues.append("发现重复索引名称")
    
    # 检查表结构问题
    for table in user_tables:
        try:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            col_names = [col[1] for col in columns]
            
            # 检查是否有常用的查询字段没有索引
            common_fields = ['id', 'user_id', 'created_at', 'status', 'date', 'name']
            has_common_index = False
            
            for idx_name, tbl_name in indexes:
                if tbl_name == table:
                    # 简单检查索引名是否包含常见字段
                    if any(field in idx_name.lower() for field in common_fields):
                        has_common_index = True
                        break
            
            if not has_common_index and len(columns) > 5:
                issues.append(f"表 {table} 可能缺少常用查询字段的索引")
                
        except Exception as e:
            issues.append(f"无法分析表 {table}: {e}")
    
    if issues:
        print("发现的问题:")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
    else:
        print("✅ 未发现明显问题")
    
    print("\n" + "="*60)
    print("💡 优化建议")
    print("="*60)
    
    suggestions = []
    
    # 基于发现的表生成建议
    if large_tables:
        suggestions.append(f"🔥 优先优化大表: {', '.join(large_tables[:3])}")
    
    # 检查特定业务表
    business_tables = ['matches', 'user_login_logs', 'betting_orders', 'payment_transactions']
    missing_business_tables = [tbl for tbl in business_tables if tbl in user_tables]
    
    if missing_business_tables:
        suggestions.append(f"📊 确保核心业务表有索引: {', '.join(missing_business_tables)}")
    
    # 通用建议
    suggestions.extend([
        "🚀 为经常用于WHERE条件的字段添加索引",
        "📈 为大表的JOIN字段添加复合索引", 
        "⚡ 定期执行VACUUM和ANALYZE优化",
        "🔍 监控慢查询并针对性优化",
        "💾 考虑分区大表以提高性能"
    ])
    
    for suggestion in suggestions:
        print(f"   • {suggestion}")
    
    print("\n" + "="*60)
    print("📋 详细表分析")
    print("="*60)
    
    # 显示前10个最大表的详细信息
    print(f"{'排名':<4} {'表名':<20} {'记录数':>12} {'索引数':>8} {'预估大小':>10}")
    print("-"*60)
    
    for i, (table, count) in enumerate(table_stats[:10], 1):
        if isinstance(count, int):
            idx_count = len(index_by_table.get(table, []))
            # 粗略估算表大小 (假设每条记录平均1KB)
            estimated_size = count / 1024
            if estimated_size > 1024:
                size_str = f"{estimated_size/1024:.1f}MB"
            else:
                size_str = f"{estimated_size:.0f}KB"
            
            print(f"{i:<4} {table:<20} {count:>12,} {idx_count:>8} {size_str:>10}")
        else:
            print(f"{i:<4} {table:<20} {'ERROR':>12} {'N/A':>8} {'N/A':>10}")
    
    conn.close()
    
    print(f"\n🎉 数据库扫描完成!")
    print(f"⏰ 扫描时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    scan_database_health()