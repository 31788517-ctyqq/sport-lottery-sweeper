#!/usr/bin/env python3
"""
添加500彩票网数据源配置脚本
"""
import sys
import os
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from backend.database import SessionLocal
from backend.models.crawler_config import CrawlerConfig
from backend.models.crawler_source_stats import CrawlerSourceStat
from backend.models.admin_user import AdminUser

def add_500_wang_source():
    """添加500彩票网数据源"""
    db = SessionLocal()
    
    try:
        # 查找管理员用户
        admin = db.query(AdminUser).first()
        if not admin:
            print('未找到管理员用户，使用ID=1')
            admin_id = 1
        else:
            admin_id = admin.id
            print(f'找到管理员用户ID: {admin_id}')
        
        # 检查是否已存在该数据源
        existing = db.query(CrawlerConfig).filter(
            CrawlerConfig.url.contains('trade.500.com/jczq')
        ).first()
        
        if existing:
            print(f'数据源已存在，ID: {existing.id}, 名称: {existing.name}')
            return existing.id
        
        # 创建新的数据源配置
        new_source = CrawlerConfig(
            name='500彩票网-足球竞彩',
            url='https://trade.500.com/jczq/',
            source_type='website',
            description='抓取500彩票网的足球竞彩比赛数据，包括3天赛程',
            request_config={
                'headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                },
                'timeout': 30,
                'retry_times': 3
            },
            parser_config={
                'type': 'jczq_parser',
                'selectors': {
                    'match_list': '.match-list',
                    'match_item': '.match-item'
                }
            },
            schedule_config={
                'enabled': True,
                'interval_minutes': 60
            },
            intelligence_config={
                'auto_analysis': True,
                'quality_threshold': 0.7
            },
            is_active=True,
            created_by=admin_id
        )
        
        db.add(new_source)
        db.flush()  # 获取ID但不提交
        source_id = new_source.id
        
        # 创建初始统计数据
        source_stat = CrawlerSourceStat(
            source_id=source_id,
            date=datetime.utcnow().date(),
            source_name=new_source.name
        )
        
        db.add(source_stat)
        db.commit()
        
        print(f'✅ 成功创建数据源配置')
        print(f'   数据源ID: {source_id}')
        print(f'   名称: {new_source.name}')
        print(f'   网址: {new_source.url}')
        print(f'   类型: {new_source.source_type}')
        
        return source_id
        
    except Exception as e:
        db.rollback()
        print(f'❌ 创建数据源失败: {str(e)}')
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    add_500_wang_source()