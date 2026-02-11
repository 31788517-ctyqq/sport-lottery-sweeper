"""
数据库初始化脚本
确保所有模型表都被正确创建
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 设置环境变量以使用正确的数据库
os.environ.setdefault('DATABASE_URL', 'sqlite:///./sport_lottery.db')
os.environ.setdefault('ASYNC_DATABASE_URL', 'sqlite+aiosqlite:///./sport_lottery.db')

from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from backend.database import Base
from backend.models import *

# 确保所有模型都被导入
from backend.models.data_sources import DataSource
from backend.models.matches import FootballMatch
from backend.models.odds_companies import OddsCompany
from backend.models.sp_records import SPRecord
from backend.models.sp_modification_logs import SPModificationLog
from backend.models.draw_feature import DrawFeature
from backend.models.draw_training_job import DrawTrainingJob
from backend.models.draw_model_version import DrawModelVersion
from backend.models.draw_prediction_result import DrawPredictionResult
from backend.models.crawler_tasks import CrawlerTask
from backend.models.headers import RequestHeader
from backend.models.ip_pool import IPPool

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sport_lottery.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """初始化数据库，创建所有表"""
    print("🔍 检查数据库中已有的表...")
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    print(f"📋 当前数据库表: {existing_tables}")
    
    print("\n🔄 开始创建数据库表...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 检查创建后的表
    updated_tables = inspector.get_table_names()
    print(f"📋 更新后数据库表: {updated_tables}")
    
    # 检查必需的表是否存在
    required_tables = ['crawler_tasks', 'request_headers', 'ip_pools']
    missing_tables = [table for table in required_tables if table not in updated_tables]
    
    if missing_tables:
        print(f"❌ 缺少表: {missing_tables}")
        return False
    else:
        print("✅ 所有必需的表都已创建成功!")
        return True

if __name__ == "__main__":
    print("🚀 开始数据库初始化...")
    success = init_db()
    
    if success:
        print("\n🎉 数据库初始化完成!")
    else:
        print("\n❌ 数据库初始化失败!")
        sys.exit(1)