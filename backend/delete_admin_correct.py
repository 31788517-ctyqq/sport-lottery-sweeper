import sys
from pathlib import Path
import sqlite3
import logging
logger = logging.getLogger(__name__)

def delete_admin_user():
    """删除admin用户"""
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
    
    try:
        # 删除admin用户
        cursor.execute("DELETE FROM users WHERE username = 'admin'")
        deleted_count = cursor.rowcount
        logger.debug(f"Deleted {deleted_count} admin user(s)")
        
        # 提交更改
        conn.commit()
        
    except Exception as e:
        logger.debug(f"Error deleting admin user: {e}")
        conn.rollback()
    finally:
        # 关闭连接
        conn.close()

if __name__ == "__main__":
    delete_admin_user()