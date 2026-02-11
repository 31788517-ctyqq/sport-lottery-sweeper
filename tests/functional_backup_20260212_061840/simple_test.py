import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置环境变量
os.environ["DATABASE_URL"] = f"sqlite:///{os.path.join(os.path.dirname(os.path.abspath(__file__)), 'simple_test.db')}"
print("Setting environment variable for DATABASE_URL")

# 导入模型
from backend.models import Base
print(f"Number of tables in metadata: {len(Base.metadata.tables)}")

# 创建引擎和表
test_engine = create_engine(
    os.environ["DATABASE_URL"],
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

print("Creating tables...")
Base.metadata.create_all(bind=test_engine)
print("Tables created!")

# 现在检查数据库
with test_engine.connect() as conn:
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")).fetchall()
    tables = [r[0] for r in result]
    print(f"Tables in database: {tables}")
    print(f"'users' table exists: {'users' in tables}")

# 现在导入应用 - 这可能会导致问题
print("Importing backend.main...")
from backend.main import app
print("App imported successfully!")

# 再次检查数据库
with test_engine.connect() as conn:
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")).fetchall()
    tables = [r[0] for r in result]
    print(f"Tables in database after importing app: {tables}")
    print(f"'users' table exists after importing app: {'users' in tables}")
