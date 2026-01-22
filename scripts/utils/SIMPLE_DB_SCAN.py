# 体育彩票扫盘系统 - 简单数据库扫描
# 复制到Python中直接执行

import sqlite3
import os

print("🔍 数据库扫描开始")
print("="*50)

db_path = "sport_lottery.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 基本检查
print("📊 基本检查:")
size = os.path.getsize(db_path)
print(f"   文件大小: {size/(1024*1024):.2f} MB")

# 表数量
cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
table_count = cursor.fetchone()[0]
print(f"   表数量: {table_count}")

# 获取表名
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]
print(f"   用户表: {len(tables)} 个")

print("\n📋 表记录数 (前15个):")
stats = []
for table in tables[:15]:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        stats.append((table, count))
        print(f"   {table:<20} : {count:>8,} 条")
    except:
        print(f"   {table:<20} : ERROR")

print("\n📊 索引统计:")
cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%'")
index_count = cursor.fetchone()[0]
print(f"   总索引数: {index_count}")

# 按表统计索引
cursor.execute("SELECT tbl_name, COUNT(*) FROM sqlite_master WHERE type='index' AND name NOT LIKE 'sqlite_%' GROUP BY tbl_name ORDER BY COUNT(*) DESC LIMIT 10")
print("   各表索引数 (Top 10):")
for tbl_name, idx_count in cursor.fetchall():
    print(f"   {tbl_name:<20} : {idx_count:>3} 个索引")

# 检查大表
print("\n🔍 大表识别 (>1万条):")
large_tables = []
for table, count in stats:
    if count > 10000:
        large_tables.append((table, count))
        print(f"   🔴 {table:<20} : {count:>8,} 条 (需优化)")
    elif count > 1000:
        print(f"   🟡 {table:<20} : {count:>8,} 条")
    else:
        print(f"   ⚪ {table:<20} : {count:>8,} 条")

# 检查可能缺少索引的表
print("\n⚠️  可能缺少索引的表:")
missing_index_tables = []
for table, count in stats:
    if count > 5000:  # 大于5000条的表应该有索引
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND tbl_name=? AND name NOT LIKE 'sqlite_%'", (table,))
        idx_count = cursor.fetchone()[0]
        if idx_count < 2:  # 少于2个索引
            missing_index_tables.append((table, count, idx_count))
            print(f"   ❌ {table:<20} : {count:>8,} 条, 仅{idx_count}个索引")

# 检查核心业务表
core_tables = ['users', 'matches', 'user_login_logs', 'betting_orders', 'payment_transactions', 'leagues', 'teams']
print("\n🎯 核心业务表状态:")
for core_table in core_tables:
    if core_table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {core_table}")
        count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index' AND tbl_name=?", (core_table,))
        idx_count = cursor.fetchone()[0]
        print(f"   ✅ {core_table:<20} : {count:>8,} 条, {idx_count:>2} 个索引")
    else:
        print(f"   ❌ {core_table:<20} : 表不存在!")

# 优化建议
print("\n💡 优化建议:")
if large_tables:
    print(f"   1. 🔥 优先优化大表: {', '.join([t[0] for t in large_tables[:3]])}")
if missing_index_tables:
    print(f"   2. 🎯 为缺少索引的表添加索引: {', '.join([t[0] for t in missing_index_tables[:3]])}")
print("   3. 🚀 确保核心业务表有足够索引")
print("   4. ⚡ 定期执行 VACUUM 和 ANALYZE")
print("   5. 📊 监控查询性能，针对慢查询优化")

# 检查视图
cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='view'")
view_count = cursor.fetchone()[0]
print(f"\n📊 视图数量: {view_count}")

if view_count > 0:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
    views = [row[0] for row in cursor.fetchall()]
    print("   现有视图:")
    for view in views:
        print(f"      • {view}")

conn.close()
print("\n✅ 扫描完成!")