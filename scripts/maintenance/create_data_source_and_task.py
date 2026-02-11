"""
创建数据源和爬虫任务
"""
import sqlite3
import json
import os
import sys

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database import engine, SessionLocal
from models.data_sources import DataSource
from models.crawler_tasks import CrawlerTask

# 创建数据库会话
db = SessionLocal()

try:
    # 1. 检查并创建500万彩票数据源
    existing_source = db.query(DataSource).filter(DataSource.name.like('%500%')).first()
    
    if existing_source:
        print(f'✓ 500万彩票数据源已存在: ID={existing_source.id}, 名称={existing_source.name}')
        source_id = existing_source.id
    else:
        print('创建500万彩票数据源...')
        
        # 配置信息
        config = {
            'source_type': 'web_scraper',
            'data_type': 'lottery_schedule',
            'parser_type': 'html_parser',
            'update_frequency': 'daily',
            'timeout': 30,
            'retry_count': 3,
            'headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }
        
        # 创建数据源
        new_source = DataSource(
            name='500万彩票',
            type='web',
            status=True,
            url='https://trade.500.com/jczq/',
            config=json.dumps(config, ensure_ascii=False),
            created_by=1
        )
        
        db.add(new_source)
        db.commit()
        db.refresh(new_source)
        
        source_id = new_source.id
        print(f'✓ 500万彩票数据源创建成功: ID={source_id}')
    
    # 2. 检查爬虫任务表是否存在
    try:
        cursor = engine.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='crawler_tasks'")
        table_exists = cursor.fetchone() is not None
        
        if not table_exists:
            print('⚠ crawler_tasks 表不存在，跳过创建爬虫任务')
        else:
            # 检查并创建爬虫任务
            existing_task = db.query(CrawlerTask).filter(CrawlerTask.name.like('%500%')).first()
            
            if existing_task:
                print(f'✓ 爬虫任务已存在: ID={existing_task.id}, 名称={existing_task.name}')
            else:
                print('创建爬虫任务...')
                
                # 任务配置
                task_config = {
                    'days': 3,
                    'data_type': 'lottery_schedule',
                    'source_url': 'https://trade.500.com/jczq/',
                    'parse_rules': {
                        'match_id': '.match-id',
                        'league': '.league-name',
                        'home_team': '.home-team',
                        'away_team': '.away-team',
                        'match_time': '.match-time',
                        'odds': '.odds-data'
                    }
                }
                
                new_task = CrawlerTask(
                    name='从500抓取近三天比赛赛程',
                    source_id=source_id,
                    task_type='crawl',
                    cron_expression='0 8 * * *',  # 每天8点执行
                    is_active=True,
                    status='stopped',
                    config=task_config,
                    created_by=1
                )
                
                db.add(new_task)
                db.commit()
                db.refresh(new_task)
                
                print(f'✓ 爬虫任务创建成功: ID={new_task.id}, 名称={new_task.name}')
    
    except Exception as e:
        print(f'⚠ 检查爬虫任务时出错: {e}')
    
    print('\n=== 操作完成 ===')
    print(f'数据源ID: {source_id}')
    print('请访问前端页面查看效果')
    
except Exception as e:
    print(f'操作失败: {e}')
    import traceback
    traceback.print_exc()
finally:
    db.close()
