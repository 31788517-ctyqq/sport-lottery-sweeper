"""
测试数据库表关系
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.models.base import Base
from backend.models.match import Match
from backend.models.odds import Odds
from backend.config import settings
from sqlalchemy import create_engine, event

def test_relationships():
    """测试表关系"""
    print("正在测试表关系...")
    
    # 创建引擎
    engine = create_engine(settings.DATABASE_URL, echo=True)
    
    # 启用SQLite外键支持
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        if dbapi_connection.__class__.__name__ == "Connection":
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
    
    # 尝试创建表
    try:
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)
        print("表创建成功！")
    except Exception as e:
        print(f"表创建失败: {e}")
        return False
    
    # 检查Match和Odds表是否存在
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    print(f"数据库中的表: {tables}")
    
    if 'matches' in tables and 'odds' in tables:
        print("matches和odds表都存在")
        
        # 检查外键约束
        fk_constraints = inspector.get_foreign_keys('odds')
        print(f"odds表的外键约束: {fk_constraints}")
        
        return True
    else:
        print("缺少必要的表")
        return False

if __name__ == "__main__":
    test_relationships()