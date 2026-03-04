import sys
from pathlib import Path
from sqlalchemy import create_engine

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.resolve()
sys.path.insert(0, str(project_root))

# 导入所有模型以确保 Base.metadata 包含所有表定义
from backend.models import Base
from backend.config import settings

def init_db():
    """初始化数据库表"""
    print("正在创建数据库表...")
    try:
        engine = create_engine(settings.DATABASE_URL, echo=False)
        Base.metadata.create_all(bind=engine)
        print("数据库表创建成功！")
    except Exception as e:
        print(f"创建数据库表时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()
