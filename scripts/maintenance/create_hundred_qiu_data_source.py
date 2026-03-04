"""
创建100qiu数据源配置和任务
用于将 https://m.100qiu.com/api/dcListBasic?dateTime=26011 的数据导入数据库
"""
import sys
import os
from datetime import datetime
import asyncio

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_db
from backend.models.data_sources import DataSource
from backend.services.sp_management_service import SPManagementService


def create_hundred_qiu_data_source():
    """创建100qiu数据源配置"""
    # 获取数据库会话
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # 检查是否已存在同名数据源
        existing_source = db.query(DataSource).filter(
            DataSource.name == '100qiu竞彩基础数据'
        ).first()
        
        if existing_source:
            print("数据源已存在，ID:", existing_source.id)
            return existing_source.id
        
        # 创建数据源配置
        sp_service = SPManagementService(db)
        
        from backend.schemas.sp_management import DataSourceCreate
        data_source_data = DataSourceCreate(
            name="100qiu竞彩基础数据",
            type="api",
            url="https://m.100qiu.com/api/dcListBasic",
            status=True,
            config={
                "params": {
                    "dateTime": "26011"
                },
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Accept": "application/json, text/plain, */*",
                    "Referer": "https://m.100qiu.com/"
                },
                "method": "GET",
                "data_source_type": "hundred_qiu",
                "cron_expression": "0 2 * * *"  # 每天凌晨2点执行
            }
        )
        
        created_source = sp_service.create_data_source(data_source_data, created_by=1)
        print(f"成功创建数据源，ID: {created_source.id}")
        return created_source.id
        
    except Exception as e:
        print(f"创建数据源失败: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def test_data_source_connection(source_id: int):
    """测试数据源连接"""
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        sp_service = SPManagementService(db)
        result = sp_service.test_data_source(source_id)
        print(f"数据源连接测试结果: {result}")
        return result
    except Exception as e:
        print(f"测试数据源连接失败: {e}")
        return None
    finally:
        db.close()


async def fetch_and_save_data():
    """获取100qiu数据并保存到数据库"""
    from backend.scrapers.hundred_qiu_scraper import HundredQiuScraper
    
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        scraper = HundredQiuScraper()
        # 使用异步方法保存数据
        count = await scraper.save_to_database(db, "26011")
        return count
    except Exception as e:
        print(f"获取并保存数据失败: {e}")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    print("开始配置100qiu数据源...")
    
    # 创建数据源
    source_id = create_hundred_qiu_data_source()
    
    if source_id:
        print("\n数据源创建成功!")
        print(f"数据源ID: {source_id}")
        
        # 测试数据源连接
        print("\n正在测试数据源连接...")
        test_result = test_data_source_connection(source_id)
        
        if test_result and test_result.get("success"):
            print("连接测试成功!")
        else:
            print("连接测试可能失败，请检查网络连接和API可用性")
        
        # 获取并保存数据
        print("\n正在获取100qiu数据并保存到数据库...")
        
        # 使用asyncio运行异步函数
        count = asyncio.run(fetch_and_save_data())
        
        if count > 0:
            print(f"\n成功导入 {count} 条比赛数据!")
            print("数据源配置和数据导入已完成！")
        else:
            print("\n数据导入可能失败，请检查网络连接和API可用性")
    else:
        print("数据源创建失败，请检查数据库连接和配置")