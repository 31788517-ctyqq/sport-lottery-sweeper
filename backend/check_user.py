"""
检查用户脚本
"""
import sys
from pathlib import Path
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

def check_admin_user():
    cursor = conn.cursor()
    cursor.execute("SELECT username, password_hash FROM users WHERE username = 'admin'")
    result = cursor.fetchone()
    if result:
        logger.debug(f"User: {result[0]}")
        logger.debug(f"Hash: {result[1]}")
    else:
        logger.debug("Admin user not found")
    conn.close()

if __name__ == "__main__":
    check_admin_user()