"""
简化版前台用户模拟数据生成脚本
用于测试和演示前台用户管理功能
"""

import json
import random
import sys
import os
from datetime import datetime, timedelta

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from backend.config import settings

def clear_mock_data(engine):
    """清理模拟数据"""
    print("开始清理模拟数据...")
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM users WHERE role = 'regular_user'"))
        conn.commit()
    print("模拟数据清理完成")

def create_mock_frontend_users(engine, num_users: int = 10):
    """创建前台用户模拟数据"""
    print(f"开始创建 {num_users} 个前台用户模拟数据...")
    
    with engine.connect() as conn:
        for i in range(1, num_users + 1):
            # 生成用户名和邮箱
            username = f"frontend_user_{i:03d}"
            email = f"frontend_user_{i:03d}@example.com"
            
            # 为notification_preferences提供一个简单的字典并转换为JSON字符串
            notification_prefs = json.dumps({
                "match_alerts": random.choice([True, False]),
                "prediction_reminders": random.choice([True, False]),
                "newsletter": random.choice([True, False])
            })
            
            # 用户配置并转换为JSON字符串
            user_config = json.dumps({
                "theme": random.choice(["light", "dark"]),
                "language": random.choice(["zh-CN", "en-US"]),
                "timezone": random.choice(["Asia/Shanghai", "UTC"])
            })
            
            # 使用原始SQL插入 - 包含所有非空字段
            insert_sql = """
            INSERT INTO users (
                username, email, password_hash, role, status, is_verified, 
                is_online, user_type, timezone, language, notification_preferences,
                config, login_count, followers_count, following_count,
                last_login_at, created_at, updated_at, phone, avatar_url
            ) VALUES (
                :username, :email, :password_hash, :role, :status, :is_verified,
                :is_online, :user_type, :timezone, :language, :notification_preferences,
                :config, :login_count, :followers_count, :following_count,
                :last_login_at, :created_at, :updated_at, :phone, :avatar_url
            )
            """
            
            conn.execute(text(insert_sql), {
                "username": username,
                "email": email,
                "password_hash": "mock_hash_" + str(i),
                "role": "regular_user",
                "status": "active",
                "is_verified": True,
                "is_online": False,
                "user_type": "normal",
                "timezone": "UTC",
                "language": "zh",
                "notification_preferences": notification_prefs,
                "config": user_config,
                "login_count": 0,
                "followers_count": 0,
                "following_count": 0,
                "last_login_at": datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                "created_at": datetime.utcnow() - timedelta(days=random.randint(30, 365)),
                "updated_at": datetime.utcnow(),
                "phone": f"1380013800{i}",
                "avatar_url": f"https://example.com/avatars/user{i}.jpg"
            })
        
        conn.commit()
    
    print(f"成功创建 {num_users} 个前台用户模拟数据")

def main(action: str = "create"):
    """主函数"""
    # 获取数据库URL - 使用同步URL
    db_url = settings.DATABASE_URL
    
    # 创建同步引擎
    engine = create_engine(db_url, echo=False)
    
    try:
        if action == "clear":
            clear_mock_data(engine)
        elif action == "create":
            clear_mock_data(engine)  # 先清理再创建
            create_mock_frontend_users(engine)
        elif action == "both":
            clear_mock_data(engine)
            create_mock_frontend_users(engine)
        else:
            print(f"未知操作: {action}")
            print("支持的操作: clear, create, both")
    finally:
        engine.dispose()

if __name__ == "__main__":
    # 获取命令行参数
    if len(sys.argv) > 1:
        action = sys.argv[1]
    else:
        action = "create"
    
    main(action)