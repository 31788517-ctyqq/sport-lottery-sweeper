import sys
from pathlib import Path
import sqlite3
import logging
logger = logging.getLogger(__name__)

# 添加backend目录到Python路径
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# 导入数据库工具
try:
    from backend.database_utils import get_db_connection
    conn = get_db_connection()
except ImportError:
    # 回退方案
    import sqlite3
    conn = sqlite3.connect('data/sport_lottery.db')
cursor = conn.cursor()

# 删除admin用户
cursor.execute("DELETE FROM users WHERE username = 'admin'")
conn.commit()

logger.debug(f"Deleted {cursor.rowcount} admin user(s)")

# 关闭连接
conn.close()