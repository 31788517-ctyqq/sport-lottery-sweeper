#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SP管理系统数据库迁移脚本
创建足球SP管理相关的数据表
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.models import init_db, db
from backend.models.sp_models import (
    DataSource, FootballMatch, OddsCompany, 
    SPRecord, SPModificationLog
)

def backup_existing_data():
    """备份现有数据（如果存在）"""
    print("🔍 检查是否需要数据备份...")
    try:
        # 这里可以添加数据备份逻辑
        # 比如导出现有Match表数据到临时表
        pass
    except Exception as e:
        print(f"⚠️  备份检查失败: {e}")

def check_table_exists(table_name):
    """检查表是否已存在"""
    try:
        result = db.session.execute(text(f"""
            SELECT COUNT(*) 
            FROM information_schema.tables 
            WHERE table_schema = DATABASE() 
            AND table_name = '{table_name}'
        """))
        return result.scalar() > 0
    except Exception:
        return False

def drop_existing_tables():
    """删除已存在的表（如果存在冲突）"""
    tables_to_drop = [
        'sp_modification_logs',
        'sp_records', 
        'odds_companies',
        'football_matches',
        'data_sources'
    ]
    
    print("🗑️  清理现有表...")
    for table_name in tables_to_drop:
        if check_table_exists(table_name):
            try:
                db.session.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
                print(f"   ✅ 已删除表: {table_name}")
            except Exception as e:
                print(f"   ❌ 删除表 {table_name} 失败: {e}")
    
    db.session.commit()

def create_sp_tables():
    """创建SP管理相关表"""
    print("🏗️  开始创建SP管理数据表...")
    
    try:
        # 创建所有表
        db.create_all()
        print("   ✅ 数据表创建完成")
        
        # 验证表是否创建成功
        tables_created = [
            ('data_sources', DataSource.__table__),
            ('football_matches', FootballMatch.__table__),
            ('odds_companies', OddsCompany.__table__),
            ('sp_records', SPRecord.__table__),
            ('sp_modification_logs', SPModificationLog.__table__)
        ]
        
        print("\n📋 验证表创建状态:")
        for table_name, table_obj in tables_created:
            if check_table_exists(table_name):
                print(f"   ✅ {table_name} - 创建成功")
                # 显示表结构
                columns = [col.name for col in table_obj.columns]
                print(f"      字段: {', '.join(columns)}")
            else:
                print(f"   ❌ {table_name} - 创建失败")
                
        return True
        
    except SQLAlchemyError as e:
        print(f"❌ 创建表失败: {e}")
        db.session.rollback()
        return False
    except Exception as e:
        print(f"❌ 未知错误: {e}")
        db.session.rollback()
        return False

def create_indexes():
    """创建索引以优化查询性能"""
    print("\n📇 创建数据库索引...")
    
    indexes = [
        # DataSource 索引
        "CREATE INDEX idx_data_source_status ON data_sources(status)",
        "CREATE INDEX idx_data_source_type ON data_sources(type)",
        "CREATE INDEX idx_data_source_last_update ON data_sources(last_update)",
        
        # FootballMatch 索引
        "CREATE INDEX idx_match_status ON football_matches(status)",
        "CREATE INDEX idx_match_time ON football_matches(match_time)",
        "CREATE INDEX idx_match_league ON football_matches(league)",
        "CREATE INDEX idx_match_teams ON football_matches(home_team, away_team)",
        "CREATE INDEX idx_match_date_range ON football_matches(match_time, status)",
        
        # OddsCompany 索引
        "CREATE INDEX idx_company_status ON odds_companies(status)",
        
        # SPRecord 索引
        "CREATE INDEX idx_sp_match_id ON sp_records(match_id)",
        "CREATE INDEX idx_sp_company_id ON sp_records(company_id)",
        "CREATE INDEX idx_sp_recorded_at ON sp_records(recorded_at)",
        "CREATE INDEX idx_sp_value ON sp_records(sp_value)",
        "CREATE INDEX idx_sp_composite ON sp_records(match_id, company_id, handicap_type, handicap_value)",
        "CREATE INDEX idx_sp_time_range ON sp_records(recorded_at, match_id)",
        
        # SPModificationLog 索引
        "CREATE INDEX idx_log_sp_record_id ON sp_modification_logs(sp_record_id)",
        "CREATE INDEX idx_log_modified_at ON sp_modification_logs(modified_at)",
        "CREATE INDEX idx_log_modified_by ON sp_modification_logs(modified_by)"
    ]
    
    success_count = 0
    for index_sql in indexes:
        try:
            db.session.execute(text(index_sql))
            index_name = index_sql.split('INDEX')[1].split('ON')[0].strip()
            print(f"   ✅ 创建索引: {index_name}")
            success_count += 1
        except Exception as e:
            print(f"   ⚠️  索引创建失败: {index_sql[:50]}... - {e}")
    
    db.session.commit()
    print(f"\n📊 索引创建完成: {success_count}/{len(indexes)} 个成功")

def insert_default_data():
    """插入默认数据"""
    print("\n🌱 插入默认数据...")
    
    try:
        # 插入默认赔率公司
        default_companies = [
            {
                'name': '竞彩官方',
                'code': 'JC_OFFICIAL',
                'website': 'https://www.lottery.gov.cn/',
                'status': True
            },
            {
                'name': '威廉希尔',
                'code': 'WILLIAM_HILL',
                'website': 'https://www.williamhill.com/',
                'status': True
            },
            {
                'name': '立博',
                'code': 'LADBROKES',
                'website': 'https://www.ladbrokes.com/',
                'status': True
            },
            {
                'name': 'Bet365',
                'code': 'BET365',
                'website': 'https://www.bet365.com/',
                'status': True
            },
            {
                'name': '澳门彩票',
                'code': 'MACAU_LOTTERY',
                'website': 'https://www.macauslot.com/',
                'status': True
            }
        ]
        
        for company_data in default_companies:
            existing = OddsCompany.query.filter_by(code=company_data['code']).first()
            if not existing:
                company = OddsCompany(**company_data)
                db.session.add(company)
                print(f"   ✅ 添加公司: {company_data['name']}")
        
        # 插入示例数据源
        default_sources = [
            {
                'name': '竞彩官方API',
                'type': 'api',
                'url': 'https://api.jczq.com/v1/odds',
                'status': True,
                'config': '{"headers": {"Authorization": "Bearer token"}, "timeout": 30}',
                'description': '竞彩官方提供的实时赔率API接口'
            },
            {
                'name': '本地比赛数据文件',
                'type': 'file', 
                'url': '/data/matches/football_matches.json',
                'status': True,
                'config': '{"encoding": "utf-8", "auto_reload": true}',
                'description': '本地存储的足球比赛数据文件'
            },
            {
                'name': 'SP值历史数据',
                'type': 'file',
                'url': '/data/sp/historical_sp.csv', 
                'status': False,
                'config': '{"delimiter": ",", "encoding": "utf-8"}',
                'description': '历史SP值数据文件，用于分析'
            }
        ]
        
        for source_data in default_sources:
            existing = DataSource.query.filter_by(name=source_data['name']).first()
            if not existing:
                source = DataSource(**source_data)
                db.session.add(source)
                print(f"   ✅ 添加数据源: {source_data['name']}")
        
        db.session.commit()
        print("\n✅ 默认数据插入完成")
        
    except Exception as e:
        print(f"❌ 默认数据插入失败: {e}")
        db.session.rollback()

def verify_installation():
    """验证安装结果"""
    print("\n🔍 验证安装结果...")
    
    try:
        # 检查表记录数
        stats = {
            '数据源': DataSource.query.count(),
            '比赛信息': FootballMatch.query.count(), 
            '赔率公司': OddsCompany.query.count(),
            'SP记录': SPRecord.query.count(),
            '修改日志': SPModificationLog.query.count()
        }
        
        print("📊 数据统计:")
        for table_name, count in stats.items():
            print(f"   {table_name}: {count} 条记录")
        
        # 检查外键关系
        companies = OddsCompany.query.all()
        sources = DataSource.query.all()
        
        print(f"\n🔗 关联检查:")
        print(f"   可用赔率公司: {len(companies)} 家")
        for company in companies:
            print(f"     - {company.name} ({company.code})")
        
        print(f"   可用数据源: {len(sources)} 个")
        for source in sources:
            print(f"     - {source.name} ({source.type})")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def create_migration_log():
    """创建迁移日志"""
    log_content = f"""
# SP管理系统数据库迁移日志

迁移时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
迁移版本: 001_create_sp_tables.py
迁移描述: 创建足球SP管理相关的基础数据表

## 创建的表
1. data_sources - 数据源配置表
2. football_matches - 比赛信息表  
3. odds_companies - 赔率公司表
4. sp_records - SP值记录表
5. sp_modification_logs - SP值修改日志表

## 默认数据
- 5家赔率公司 (竞彩官方、威廉希尔、立博、Bet365、澳门彩票)
- 3个数据源 (API接口和文件数据源)

## 注意事项
- 此迁移不会删除现有数据
- 建议在测试环境先验证
- 生产环境请做好数据备份
"""
    
    log_file = os.path.join(project_root, 'migrations', 'migration_log.md')
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write(log_content)
    
    print(f"\n📝 迁移日志已保存: {log_file}")

def main():
    """主函数"""
    print("🚀 开始SP管理系统数据库迁移...")
    print("=" * 50)
    
    try:
        # 初始化数据库连接
        print("🔌 初始化数据库连接...")
        init_db()
        print("   ✅ 数据库连接成功")
        
        # 备份现有数据
        backup_existing_data()
        
        # 创建表
        if not create_sp_tables():
            print("❌ 表创建失败，迁移终止")
            return False
        
        # 创建索引
        create_indexes()
        
        # 插入默认数据
        insert_default_data()
        
        # 验证安装
        if not verify_installation():
            print("⚠️  安装验证失败，但表创建成功")
        
        # 创建迁移日志
        create_migration_log()
        
        print("\n" + "=" * 50)
        print("🎉 数据库迁移完成！")
        print("\n📋 后续步骤:")
        print("1. 检查前端路由配置是否正确")
        print("2. 配置数据源API接口或文件路径")
        print("3. 导入历史比赛数据和SP值数据")
        print("4. 配置用户权限和角色")
        print("5. 测试各项功能是否正常")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 迁移过程出现严重错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        try:
            db.session.close()
        except:
            pass

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)