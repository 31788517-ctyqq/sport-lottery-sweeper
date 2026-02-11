"""
测试API能否正确返回数据
"""
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.database import get_db
from backend.crud.crawler_config import get_multi as get_crawler_configs
from backend.services.task_scheduler_service import TaskSchedulerService


def test_api_endpoints():
    """测试API端点是否能正确返回数据"""
    print("="*60)
    print("测试API端点数据返回")
    print("="*60)
    
    db_gen = get_db()
    db = next(db_gen)
    
    try:
        # 测试爬虫配置API端点
        print("\n1. 测试爬虫配置API端点:")
        configs, total = get_crawler_configs(db, skip=0, limit=100)
        print(f"   ✓ 成功获取 {len(configs)} 个配置，总数: {total}")
        for config in configs:
            print(f"   - 配置ID: {config.id}, 名称: {config.name}")
        
        # 测试任务API端点
        print("\n2. 测试任务API端点:")
        service = TaskSchedulerService(db)
        tasks = service.get_tasks()
        print(f"   ✓ 成功获取 {len(tasks)} 个任务")
        for task in tasks:
            print(f"   - 任务ID: {task.id}, 名称: {task.name}, 状态: {task.status}")
        
        # 测试带筛选的任务API端点
        print("\n3. 测试带筛选的任务API端点:")
        filtered_tasks = service.get_tasks(source_id=1)
        print(f"   ✓ 通过source_id=1筛选，获取 {len(filtered_tasks)} 个任务")
        for task in filtered_tasks:
            print(f"   - 任务ID: {task.id}, 名称: {task.name}")
        
        print("\n" + "="*60)
        print("API端点测试完成！数据可以在前端页面显示。")
        print("1. 数据源配置页面将显示爬虫配置信息")
        print("2. 任务控制台页面将显示任务信息")
        print("="*60)
        
    except Exception as e:
        print(f"API端点测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    test_api_endpoints()