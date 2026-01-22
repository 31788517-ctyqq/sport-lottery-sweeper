# setup_alembic_initial.py
import os
import subprocess
import sys

PROJECT_DIR = r"c:\Users\11581\Downloads\sport-lottery-sweeper"
os.chdir(PROJECT_DIR)

# 1. 检查 alembic.ini 并修改 sqlalchemy.url
alembic_ini = os.path.join(PROJECT_DIR, "alembic.ini")
with open(alembic_ini, "r", encoding="utf-8") as f:
    content = f.read()
# 替换默认占位 URL 为 SQLite 绝对路径
content = content.replace(
    "sqlalchemy.url = driver://user:pass@localhost/dbname",
    "sqlalchemy.url = sqlite:///c:/Users/11581/Downloads/sport-lottery-sweeper/sport_lottery.db"
)
with open(alembic_ini, "w", encoding="utf-8") as f:
    f.write(content)
print("✅ 更新 alembic.ini 的数据库连接")

# 2. 修改 env.py 引入 Base.metadata
env_py = os.path.join(PROJECT_DIR, "alembic", "env.py")
with open(env_py, "r", encoding="utf-8") as f:
    env_content = f.read()

# 添加路径插入
import_stmt = (
    "import os\n"
    "import sys\n"
    "sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))\n"
    "\n"
)

# 替换 target_metadata
if "target_metadata" in env_content:
    env_content = env_content.replace(
        "target_metadata = None",
        "from backend.models.base import Base\n"
        "target_metadata = Base.metadata"
    )
else:
    env_content += "\nfrom backend.models.base import Base\n" "target_metadata = Base.metadata\n"

# 确保 import_stmt 在文件顶部
if "sys.path.insert" not in env_content:
    env_content = import_stmt + env_content

with open(env_py, "w", encoding="utf-8") as f:
    f.write(env_content)
print("✅ 更新 alembic/env.py 的 target_metadata")

# 3. 生成迁移脚本
result = subprocess.run(["alembic", "revision", "--autogenerate", "-m", "initial: import leagues, teams, matches tables"], capture_output=True, text=True)
if result.returncode != 0:
    print("❌ 生成迁移脚本失败:", result.stderr)
    sys.exit(1)
print("✅ 生成初始迁移脚本")

# 4. 应用迁移
result = subprocess.run(["alembic", "upgrade", "head"], capture_output=True, text=True)
if result.returncode != 0:
    print("❌ 应用迁移失败:", result.stderr)
    sys.exit(1)
print("✅ 应用迁移到数据库")
