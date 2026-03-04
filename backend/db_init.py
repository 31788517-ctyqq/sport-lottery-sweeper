"""
数据库初始化脚本
确保所有模型表都被正确创建
"""
import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 导入配置
try:
    from backend.config import settings
    DATABASE_URL = settings.DATABASE_URL
    ASYNC_DATABASE_URL = settings.ASYNC_DATABASE_URL
except ImportError:
    # 回退方案：手动构建数据库路径
    from backend.config import DATA_DIR, ABS_DB_PATH
    DATABASE_URL = f"sqlite:///{ABS_DB_PATH}"
    ASYNC_DATABASE_URL = f"sqlite+aiosqlite:///{ABS_DB_PATH}"

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

# 数据库配置 - 使用配置系统中的URL
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """初始化数据库，创建所有表"""
    print("Checking existing tables in database...")
    
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    print(f"Current database tables: {existing_tables}")
    
    print("\nCreating database tables...")
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    
    # 检查创建后的表
    updated_tables = inspector.get_table_names()
    print(f"Updated database tables: {updated_tables}")
    
    # 检查必需的表是否存在
    required_tables = ['crawler_tasks', 'request_headers', 'ip_pools']
    missing_tables = [table for table in required_tables if table not in updated_tables]
    
    if missing_tables:
        print(f"Missing tables: {missing_tables}")
        return False
    else:
        print("All required tables created successfully!")
        return True

if __name__ == "__main__":
    print("Starting database initialization...")
    success = init_db()
    
    if success:
        print("\nDatabase initialization completed successfully!")
    else:
        print("\nDatabase initialization failed!")
        sys.exit(1)