"""
检查数据库中的数据源记录，查看分类信息的存储方式
"""
import json
import os
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.database import engine
from backend.models.data_sources import DataSource
from sqlalchemy.orm import sessionmaker

def check_data_source_categories():
    """检查数据源记录中的分类信息"""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # 查询所有数据源
        data_sources = db.query(DataSource).all()
        
        print(f"共找到 {len(data_sources)} 条数据源记录\n")
        
        for idx, source in enumerate(data_sources, 1):
            print(f"{idx}. ID: {source.id}, Source ID: {source.source_id}, 名称: {source.name}")
            print(f"   类型: {source.type}, 状态: {source.status}")
            print(f"   地址: {source.url}")
            
            # 解析配置信息
            config_data = {}
            if source.config:
                try:
                    config_data = json.loads(source.config)
                    print(f"   配置: {config_data}")
                    
                    # 检查配置中是否包含分类信息
                    if 'category' in config_data:
                        print(f"   分类信息: {config_data['category']}")
                    else:
                        print("   配置中未找到分类信息")
                        
                except json.JSONDecodeError:
                    print(f"   配置解析失败: {source.config}")
            else:
                print("   配置为空")
            
            print("-" * 80)
            
    except Exception as e:
        print(f"查询数据源失败: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    check_data_source_categories()