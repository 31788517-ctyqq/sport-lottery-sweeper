#!/usr/bin/env python3
"""
测试模型注册和映射器配置
"""
import sys
sys.path.insert(0, '.')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, class_mapper
from models.base import Base
from models.user import User
from models.predictions import UserPrediction, Prediction

print("=== 测试模型注册 ===")

# 创建内存数据库引擎
engine = create_engine('sqlite:///:memory:')

# 创建所有表
try:
    Base.metadata.create_all(engine)
    print("✓ 数据库表创建成功")
except Exception as e:
    print(f"✗ 数据库表创建失败: {e}")
    sys.exit(1)

# 测试映射器配置
models_to_test = [User, UserPrediction, Prediction]
for model in models_to_test:
    try:
        mapper = class_mapper(model)
        print(f"✓ {model.__name__} 映射器配置成功")
    except Exception as e:
        print(f"✗ {model.__name__} 映射器配置失败: {e}")

# 测试关系
print("\n=== 测试关系 ===")
if hasattr(User, 'user_predictions'):
    rel = User.user_predictions
    print(f"✓ User.user_predictions 关系存在: {rel}")
else:
    print("✗ User.user_predictions 关系缺失")

if hasattr(UserPrediction, 'user'):
    rel = UserPrediction.user
    print(f"✓ UserPrediction.user 关系存在: {rel}")
else:
    print("✗ UserPrediction.user 关系缺失")

if hasattr(Prediction, 'user_predictions'):
    rel = Prediction.user_predictions
    print(f"✓ Prediction.user_predictions 关系存在: {rel}")
else:
    print("✗ Prediction.user_predictions 关系缺失")

# 创建一个会话并测试基本操作
Session = sessionmaker(bind=engine)
session = Session()

try:
    # 创建一个测试用户
    test_user = User(
        username='testuser',
        email='test@example.com',
        hashed_password='fakehash',
        status='active'
    )
    session.add(test_user)
    session.commit()
    print(f"✓ 用户创建成功: id={test_user.id}")
    
    # 清理
    session.query(User).delete()
    session.commit()
    print("✓ 清理成功")
    
except Exception as e:
    print(f"✗ 数据库操作失败: {e}")
    session.rollback()

print("\n=== 测试完成 ===")