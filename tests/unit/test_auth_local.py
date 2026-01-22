import sys
sys.path.insert(0, 'backend')

from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from backend.core.auth import authenticate_user, create_access_token
from datetime import timedelta

# 创建数据库会话
engine = create_engine('sqlite:///sport_lottery.db')
session = Session(bind=engine)

# 测试认证
username = 'admin'
password = 'admin123'
print(f"认证用户 {username}...")
user = authenticate_user(session, username, password)
if user:
    print(f"认证成功! 用户: {user.username}, 邮箱: {user.email}")
    # 创建令牌
    access_token = create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=15))
    print(f"访问令牌: {access_token}")
else:
    print("认证失败: 用户不存在或密码错误")
    
session.close()