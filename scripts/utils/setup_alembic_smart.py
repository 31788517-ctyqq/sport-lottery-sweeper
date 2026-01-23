# setup_alembic_smart.py
import os
import subprocess
import sys
import sqlite3

def run_cmd(cmd):
    """执行命令并返回 stdout, stderr, returncode"""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout, result.stderr, result.returncode

# 硬编码项目根目录
BASE_DIR = "D:/sport-lottery-sweeper"
os.chdir(BASE_DIR)
print(f"工作目录: {BASE_DIR}")

# 1. 检查 alembic 是否安装
stdout, stderr, code = run_cmd([sys.executable, "-m", "pip", "show", "alembic"])
if code != 0:
    print("❌ 未检测到 alembic，请先执行: pip install alembic")
    sys.exit(1)
print("✅ alembic 已安装")

# 2. 修正 alembic.ini 的 sqlalchemy.url
alembic_ini = os.path.join(BASE_DIR, "alembic.ini")
with open(alembic_ini, "r", encoding="utf-8") as f:
    content = f.read()
new_url = "sqlite:///D:/sport-lottery-sweeper/sport_lottery.db"
if "sqlite:///D:/sport-lottery-sweeper/sport_lottery.db" not in content:
    content = content.replace(
        "sqlalchemy.url = driver://user:pass@localhost/dbname",
        new_url
    )
    with open(alembic_ini, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 更新 alembic.ini 的数据库连接")
else:
    print("✅ alembic.ini 已是正确的 SQLite 路径")

# 3. 修正 env.py 引入 Base.metadata
env_py = os.path.join(BASE_DIR, "alembic", "env.py")
with open(env_py, "r", encoding="utf-8") as f:
    env_content = f.read()

import_stmt = (
    "import os\n"
    "import sys\n"
    "sys.path.insert(0, 'D:/sport-lottery-sweeper')\n"
    "\n"
)

if "from backend.models.base import Base" not in env_content:
    env_content = env_content.replace(
        "target_metadata = None",
        "from backend.models.base import Base\n"
        "target_metadata = Base.metadata"
    )
    if "sys.path.insert" not in env_content:
        env_content = import_stmt + env_content
    with open(env_py, "w", encoding="utf-8") as f:
        f.write(env_content)
    print("✅ 更新 alembic/env.py 的 target_metadata")
else:
    print("✅ alembic/env.py 已正确配置 Base.metadata")

# 4. 检查数据库是否已有表
DB_PATH = os.path.join(BASE_DIR, "sport_lottery.db")
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('leagues','teams','matches');")
existing_tables = [row[0] for row in cur.fetchall()]
conn.close()

has_tables = len(existing_tables) > 0
print(f"📋 检测到数据库中已存在的表: {existing_tables}")

# 5. 生成迁移脚本
if has_tables:
    print("⚠️ 数据库已存在表，使用空迁移接管现有结构")
    # 生成空迁移文件（不带 --empty 参数）
    stdout, stderr, code = run_cmd(["alembic", "revision", "-m", "initial_structure"])
    if code != 0:
        print("❌ 创建迁移脚本失败:", stderr)
        sys.exit(1)
    print("✅ 生成空迁移脚本")

    # 找到最新生成的版本号
    versions_dir = os.path.join(BASE_DIR, "alembic", "versions")
    py_files = [f for f in os.listdir(versions_dir) if f.endswith(".py")]
    if not py_files:
        print("❌ 未找到生成的迁移文件")
        sys.exit(1)
    latest_file = sorted(py_files)[-1]
    version_id = latest_file.split('_')[0]
    print(f"📌 版本号: {version_id}")

    # 清空 upgrade() 与 downgrade() 内容，确保为空迁移
    rev_path = os.path.join(versions_dir, latest_file)
    with open(rev_path, "r", encoding="utf-8") as f:
        content = f.read()
    # 替换 upgrade() 函数体为 pass
    content = content.replace(
        "def upgrade():\n    pass",
        "def upgrade():\n    # 空迁移，用于接管已有数据库结构\n    pass"
    )
    # 替换 downgrade() 函数体为 pass
    content = content.replace(
        "def downgrade():\n    pass",
        "def downgrade():\n    # 空迁移，无法自动降级\n    pass"
    )
    with open(rev_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("✅ 已清空迁移脚本内容，确保为空迁移")

    # 将版本号写入 alembic_version 表
    conn = sqlite3.connect("D:/sport-lottery-sweeper/sport_lottery.db")
    cur = conn.cursor()
    cur.execute("DELETE FROM alembic_version;")
    cur.execute("INSERT INTO alembic_version (version_num) VALUES (?);", (version_id,))
    conn.commit()
    conn.close()
    print(f"✅ 已将版本 {version_id} 标记为已应用")
else:
    print("ℹ️ 数据库无表，执行正常 autogenerate")
    stdout, stderr, code = run_cmd(["alembic", "revision", "--autogenerate", "-m", "initial"])
    if code != 0:
        print("❌ 生成迁移脚本失败:", stderr)
        sys.exit(1)
    print("✅ 生成初始迁移脚本")
    # 应用迁移
    stdout, stderr, code = run_cmd(["alembic", "upgrade", "head"])
    if code != 0:
        print("❌ 应用迁移失败:", stderr)
        sys.exit(1)
    print("✅ 应用迁移到数据库")

print("🎉 Alembic 初始化完成，现有表已纳入版本管理")
