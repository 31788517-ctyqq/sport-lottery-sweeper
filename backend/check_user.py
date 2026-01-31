"""
检查用户脚本
"""
import sqlite3
import logging
logger = logging.getLogger(__name__)

def check_admin_user():
    conn = sqlite3.connect('sport_lottery.db')
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