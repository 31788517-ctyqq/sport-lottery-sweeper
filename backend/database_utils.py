#!/usr/bin/env python3
"""
数据库工具模块 - 封装常用的数据库操作

注意：根据数据库路径规范，数据库文件应位于项目根目录，并通过 backend.database.DATABASE_PATH 配置。
本模块优先使用统一的 DATABASE_PATH 配置，保持向后兼容性。
"""
import sqlite3
import bcrypt
import os
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from datetime import datetime

# 优先使用统一的数据库路径配置
try:
    from backend.database import DATABASE_PATH
    # DATABASE_PATH 可能是 pathlib.Path 对象，转换为字符串
    DB_PATH = str(DATABASE_PATH)
except ImportError:
    # 回退到原来的路径查找逻辑
    # 获取项目根目录的数据库路径 - 优先使用根目录，如果不存在则使用data目录
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # 尝试多个可能的数据库路径
    possible_paths = [
        os.path.join(PROJECT_ROOT, "sport_lottery.db"),  # 根目录
        os.path.join(PROJECT_ROOT, "data", "sport_lottery.db"),  # data目录
    ]

    DB_PATH = None
    for path in possible_paths:
        if os.path.exists(path):
            DB_PATH = path
            break

    if DB_PATH is None:
        # 如果都不存在，使用根目录的默认路径
        DB_PATH = os.path.join(PROJECT_ROOT, "sport_lottery.db")

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 设置行工厂以支持字典式访问
    return conn

# 为了兼容性，添加get_db作为get_db_connection的别名
def get_db():
    """获取数据库连接（SQLAlchemy风格接口）"""
    return get_db_connection()

@contextmanager
def get_db_session():
    """数据库会话上下文管理器"""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def verify_password(password: str, password_hash: str) -> bool:
    """验证密码"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception:
        return False

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """用户认证 - 验证用户名和密码"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email, password_hash, role, status FROM admin_users WHERE username = ? AND status = 'active'",
            (username,)
        )
        user = cursor.fetchone()
        
        if user and verify_password(password, user['password_hash']):
            return {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "role": user['role'],
                "status": user['status']
            }
        return None
    finally:
        conn.close()

def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """根据ID获取用户信息"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, username, email, role, status, created_at FROM admin_users WHERE id = ?",
            (user_id,)
        )
        user = cursor.fetchone()
        return dict(user) if user else None
    finally:
        conn.close()

def get_dashboard_stats() -> Dict[str, Any]:
    """获取仪表板统计数据"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 获取用户统计
        try:
            cursor.execute("SELECT COUNT(*) as total_users FROM users WHERE status = 'active'")
            total_users = cursor.fetchone()['total_users']
        except sqlite3.OperationalError:
            total_users = 0
        
        # 获取今日比赛数量
        today = datetime.now().strftime('%Y-%m-%d')
        try:
            cursor.execute("SELECT COUNT(*) as today_matches FROM matches WHERE match_date LIKE ?", (f'{today}%',))
            today_matches = cursor.fetchone()['today_matches']
        except sqlite3.OperationalError:
            today_matches = 0
        
        # 获取活跃数据源数量
        try:
            cursor.execute("SELECT COUNT(*) as active_sources FROM crawler_sources WHERE status = 'online'")
            active_sources = cursor.fetchone()['active_sources']
        except sqlite3.OperationalError:
            active_sources = 0
        
        return {
            "total_users": total_users,
            "today_matches": today_matches,
            "active_sources": active_sources,
            "system_status": "healthy"
        }
    finally:
        conn.close()

def get_intelligence_screening_list() -> Dict[str, Any]:
    """获取情报筛选列表"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT id, title, category, priority, status, created_at FROM intelligence_data ORDER BY created_at DESC LIMIT 10"
            )
            items = [dict(row) for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            items = []
        
        return {
            "items": items,
            "total": len(items),
            "page": 1,
            "size": len(items)
        }
    finally:
        conn.close()