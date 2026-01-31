#!/usr/bin/env python3
"""
测试模型导入和映射器配置
"""
import sys
sys.path.insert(0, '.')

from sqlalchemy.orm import class_mapper

try:
    from models.user import User
    print("✓ User imported successfully")
except Exception as e:
    print(f"✗ User import failed: {e}")
    sys.exit(1)

try:
    from models.predictions import UserPrediction
    print("✓ UserPrediction imported successfully")
except Exception as e:
    print(f"✗ UserPrediction import failed: {e}")
    sys.exit(1)

try:
    from models.predictions import Prediction
    print("✓ Prediction imported successfully")
except Exception as e:
    print(f"✗ Prediction import failed: {e}")
    sys.exit(1)

# 检查映射器配置
try:
    user_mapper = class_mapper(User)
    print(f"✓ User mapper configured: {user_mapper}")
except Exception as e:
    print(f"✗ User mapper configuration failed: {e}")

try:
    user_prediction_mapper = class_mapper(UserPrediction)
    print(f"✓ UserPrediction mapper configured: {user_prediction_mapper}")
except Exception as e:
    print(f"✗ UserPrediction mapper configuration failed: {e}")

try:
    prediction_mapper = class_mapper(Prediction)
    print(f"✓ Prediction mapper configured: {prediction_mapper}")
except Exception as e:
    print(f"✗ Prediction mapper configuration failed: {e}")

# 检查关系
if hasattr(User, 'user_predictions'):
    print(f"✓ User.user_predictions relationship exists: {User.user_predictions}")
else:
    print("✗ User.user_predictions relationship missing")

if hasattr(UserPrediction, 'user'):
    print(f"✓ UserPrediction.user relationship exists: {UserPrediction.user}")
else:
    print("✗ UserPrediction.user relationship missing")

print("\nTest completed")