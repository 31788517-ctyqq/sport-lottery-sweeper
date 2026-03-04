#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据源与爬虫配置同步管理脚本
用于确保数据源和爬虫配置之间的一致性
"""
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent
if str(project_root.parent) not in sys.path:
    sys.path.insert(0, str(project_root.parent))

from sqlalchemy.orm import sessionmaker
from backend.database import engine
from backend.models.data_sources import DataSource
from backend.models.crawler_config import CrawlerConfig
from backend.models.crawler_tasks import CrawlerTask
from backend.crawler.management import (
    create_crawler_config_from_data_source,
    sync_data_source_to_crawler_config,
    sync_crawler_config_to_data_source
)
from backend.database import get_db


def check_sync_status(db_session=None):
    """检查数据源和爬虫配置的同步状态"""
    # 如果没有提供会话，则创建一个新的
    own_session = False
    if db_session is None:
        db_session = next(get_db())
        own_session = True

    try:
        # 统计数据源数量
        data_source_count = db_session.query(DataSource).count()
        print(f"数据源总数: {data_source_count}")

        # 统计爬虫配置数量
        crawler_config_count = db_session.query(CrawlerConfig).count()
        print(f"爬虫配置总数: {crawler_config_count}")

        # 统计已关联的爬虫配置数量
        linked_config_count = db_session.query(CrawlerConfig).filter(
            CrawlerConfig.source_id.isnot(None)
        ).count()
        print(f"已关联数据源的爬虫配置数: {linked_config_count}")

        # 显示未关联的数据源
        unlinked_sources = db_session.query(DataSource).outerjoin(
            CrawlerConfig, 
            DataSource.id == CrawlerConfig.source_id
        ).filter(CrawlerConfig.id.is_(None)).all()

        if unlinked_sources:
            print(f"未关联爬虫配置的数据源 ({len(unlinked_sources)}):")
            for source in unlinked_sources:
                print(f"  - ID: {source.id}, Name: {source.name}")
        else:
            print("✓ 所有数据源均已关联爬虫配置")

        # 显示没有关联数据源的爬虫配置
        unlinked_configs = db_session.query(CrawlerConfig).outerjoin(
            DataSource,
            CrawlerConfig.source_id == DataSource.id
        ).filter(
            DataSource.id.is_(None),
            CrawlerConfig.source_id.isnot(None)
        ).all()

        if unlinked_configs:
            print(f"无效关联的爬虫配置 ({len(unlinked_configs)}):")
            for config in unlinked_configs:
                print(f"  - ID: {config.id}, Name: {config.name}, Source ID: {config.source_id}")
        else:
            print("✓ 所有爬虫配置均正确关联到数据源")

        return {
            "data_source_count": data_source_count,
            "crawler_config_count": crawler_config_count,
            "linked_config_count": linked_config_count,
            "unlinked_sources": unlinked_sources,
            "unlinked_configs": unlinked_configs
        }

    finally:
        if own_session:
            db_session.close()


def sync_all_data_sources():
    """同步所有数据源到爬虫配置"""
    db = next(get_db())

    try:
        # 获取所有数据源
        data_sources = db.query(DataSource).all()
        print(f"找到 {len(data_sources)} 个数据源")

        created_configs = 0
        updated_configs = 0
        skipped_configs = 0

        for source in data_sources:
            # 检查是否已存在对应的爬虫配置
            existing_config = db.query(CrawlerConfig).filter(
                CrawlerConfig.source_id == source.id
            ).first()

            if not existing_config:
                print(f"为数据源 '{source.name}' (ID: {source.id}) 创建爬虫配置...")
                try:
                    create_crawler_config_from_data_source(db, source)
                    created_configs += 1
                except Exception as e:
                    print(f"  创建爬虫配置失败: {e}")
            else:
                print(f"为数据源 '{source.name}' (ID: {source.id}) 更新爬虫配置...")
                try:
                    sync_data_source_to_crawler_config(db, source.id)
                    updated_configs += 1
                except Exception as e:
                    print(f"  更新爬虫配置失败: {e}")

        # 提交事务
        db.commit()

        print(f"\n同步完成!")
        print(f"- 创建了 {created_configs} 个新爬虫配置")
        print(f"- 更新了 {updated_configs} 个现有爬虫配置")
        print(f"- 跳过了 0 个已有配置")

        # 再次检查同步状态
        check_sync_status(db)

        return True
    except Exception as e:
        print(f"同步过程出错: {e}")
        return False
    finally:
        db.close()


def force_resync_data_source(source_id: int):
    """强制重新同步指定的数据源"""
    db = next(get_db())

    try:
        # 获取指定数据源
        data_source = db.query(DataSource).filter(DataSource.id == source_id).first()
        if not data_source:
            print(f"❌ 数据源不存在，ID: {source_id}")
            return False

        # 删除关联的爬虫配置
        existing_config = db.query(CrawlerConfig).filter(
            CrawlerConfig.source_id == source_id
        ).first()

        if existing_config:
            print(f"删除原有爬虫配置: {existing_config.name} (ID: {existing_config.id})")
            db.delete(existing_config)

        # 重新创建爬虫配置
        print(f"为数据源 '{data_source.name}' (ID: {source_id}) 重新创建爬虫配置...")
        new_config = create_crawler_config_from_data_source(db, data_source)

        # 提交事务
        db.commit()

        print(f"✅ 强制重新同步完成，新配置ID: {new_config.id}")
        return True

    except Exception as e:
        print(f"强制重新同步过程出错: {e}")
        return False
    finally:
        db.close()


def validate_sync_integrity():
    """验证同步完整性，检查数据一致性"""
    db = next(get_db())

    try:
        issues = []

        # 检查所有数据源和其对应的爬虫配置
        sources = db.query(DataSource).all()
        for source in sources:
            config = db.query(CrawlerConfig).filter(
                CrawlerConfig.source_id == source.id
            ).first()

            if config:
                # 检查关键字段是否一致
                if source.status != config.is_active:
                    issues.append({
                        'type': 'status_mismatch',
                        'source_id': source.id,
                        'source_name': source.name,
                        'source_status': source.status,
                        'config_status': config.is_active,
                        'config_id': config.id
                    })

                if source.url != config.url:
                    issues.append({
                        'type': 'url_mismatch',
                        'source_id': source.id,
                        'source_name': source.name,
                        'source_url': source.url,
                        'config_url': config.url,
                        'config_id': config.id
                    })

        # 检查爬虫任务是否与配置关联
        tasks = db.query(CrawlerTask).filter(
            CrawlerTask.source_id.isnot(None)
        ).all()
        for task in tasks:
            config = db.query(CrawlerConfig).filter(
                CrawlerConfig.id == task.source_id
            ).first()

            if not config:
                issues.append({
                    'type': 'orphaned_task',
                    'task_id': task.id,
                    'task_name': task.name,
                    'task_source_id': task.source_id
                })

        if issues:
            print(f"发现 {len(issues)} 个同步问题:")
            for issue in issues:
                if issue['type'] == 'status_mismatch':
                    print(f"  - 数据源状态不匹配: "
                          f"数据源ID {issue['source_id']} ({issue['source_name']}) "
                          f"状态 {issue['source_status']}, "
                          f"爬虫配置ID {issue['config_id']} 状态 {issue['config_status']}")
                elif issue['type'] == 'url_mismatch':
                    print(f"  - 数据源URL不匹配: "
                          f"数据源ID {issue['source_id']} ({issue['source_name']}) "
                          f"URL {issue['source_url']}, "
                          f"爬虫配置ID {issue['config_id']} URL {issue['config_url']}")
                elif issue['type'] == 'orphaned_task':
                    print(f"  - 孤立任务: "
                          f"任务ID {issue['task_id']} ({issue['task_name']}) "
                          f"引用不存在的配置ID {issue['task_source_id']}")
        else:
            print("✅ 所有数据源和爬虫配置同步完整，无数据一致性问题")

        return issues

    finally:
        db.close()


def main():
    """主函数"""
    print("🔍 数据源与爬虫配置同步管理工具")
    print("="*60)

    # 检查当前目录
    current_dir = Path.cwd()
    print(f"📁 当前目录: {current_dir}")

    # 解析命令行参数
    if len(sys.argv) < 2:
        print("\n📖 使用方法:")
        print("  python sync_data_source_crawler_config.py status           # 检查同步状态")
        print("  python sync_data_source_crawler_config.py sync             # 同步所有数据源")
        print("  python sync_data_source_crawler_config.py resync <id>     # 强制重新同步指定数据源")
        print("  python sync_data_source_crawler_config.py validate        # 验证同步完整性")
        print("  python sync_data_source_crawler_config.py full-sync       # 完整同步（先验证再同步）")
        return 1

    command = sys.argv[1].lower()

    if command == "status":
        print("\n📋 检查同步状态...")
        check_sync_status()
    elif command == "sync":
        print("\n🔄 开始同步所有数据源...")
        success = sync_all_data_sources()
        if success:
            print("\n✅ 数据源与爬虫配置同步完成！")
        else:
            print("\n❌ 同步失败！")
            return 1
    elif command == "resync":
        if len(sys.argv) < 3:
            print("❌ 请提供数据源ID")
            print("用法: python sync_data_source_crawler_config.py resync <数据源ID>")
            return 1

        try:
            source_id = int(sys.argv[2])
            print(f"\n🔄 强制重新同步数据源 {source_id}...")
            success = force_resync_data_source(source_id)
            if success:
                print("✅ 强制重新同步完成！")
            else:
                print("❌ 强制重新同步失败！")
                return 1
        except ValueError:
            print("❌ 数据源ID必须是数字")
            return 1
    elif command == "validate":
        print("\n🔍 验证同步完整性...")
        issues = validate_sync_integrity()
        if issues:
            print(f"\n⚠️  发现 {len(issues)} 个问题，建议运行 'sync' 命令进行修复")
            return 1
        else:
            print("\n✅ 验证通过，无数据一致性问题")
    elif command == "full-sync":
        print("\n🔍 验证同步完整性...")
        issues = validate_sync_integrity()
        if issues:
            print(f"发现 {len(issues)} 个问题，开始修复...")
            print("\n🔄 开始同步所有数据源...")
            success = sync_all_data_sources()
            if success:
                print("\n✅ 完整同步完成！")
            else:
                print("\n❌ 完整同步失败！")
                return 1
        else:
            print("\n✅ 无需同步，数据已是一致的")
    else:
        print(f"❌ 未知命令: {command}")
        print("\n📖 使用方法:")
        print("  python sync_data_source_crawler_config.py status           # 检查同步状态")
        print("  python sync_data_source_crawler_config.py sync             # 同步所有数据源")
        print("  python sync_data_source_crawler_config.py resync <id>     # 强制重新同步指定数据源")
        print("  python sync_data_source_crawler_config.py validate        # 验证同步完整性")
        print("  python sync_data_source_crawler_config.py full-sync       # 完整同步（先验证再同步）")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())