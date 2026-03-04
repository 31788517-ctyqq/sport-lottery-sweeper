#!/usr/bin/env python3
"""
娴嬭瘯妯″瀷娉ㄥ唽鍜屾槧灏勫櫒閰嶇疆
"""
import sys
sys.path.insert(0, '.')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, class_mapper
from models.base import Base
from models.user import User
from models.predictions import UserPrediction, Prediction

print("=== 娴嬭瘯妯″瀷娉ㄥ唽 ===")

# 鍒涘缓鍐呭瓨鏁版嵁搴撳紩鎿?engine = create_engine('sqlite:///:memory:')

# 鍒涘缓鎵€鏈夎〃
try:
    Base.metadata.create_all(engine)
    print("SUCCESS 鏁版嵁搴撹〃鍒涘缓鎴愬姛")
except Exception as e:
    print(f"FAILED 鏁版嵁搴撹〃鍒涘缓澶辫触: {e}")
    sys.exit(1)

# 娴嬭瘯鏄犲皠鍣ㄩ厤缃?models_to_test = [User, UserPrediction, Prediction]
for model in models_to_test:
    try:
        mapper = class_mapper(model)
        print(f"SUCCESS {model.__name__} 鏄犲皠鍣ㄩ厤缃垚鍔?)
    except Exception as e:
        print(f"FAILED {model.__name__} 鏄犲皠鍣ㄩ厤缃け璐? {e}")

# 娴嬭瘯鍏崇郴
print("\n=== 娴嬭瘯鍏崇郴 ===")
if hasattr(User, 'user_predictions'):
    rel = User.user_predictions
    print(f"SUCCESS User.user_predictions 鍏崇郴瀛樺湪: {rel}")
else:
    print("FAILED User.user_predictions 鍏崇郴缂哄け")

if hasattr(UserPrediction, 'user'):
    rel = UserPrediction.user
    print(f"SUCCESS UserPrediction.user 鍏崇郴瀛樺湪: {rel}")
else:
    print("FAILED UserPrediction.user 鍏崇郴缂哄け")

if hasattr(Prediction, 'user_predictions'):
    rel = Prediction.user_predictions
    print(f"SUCCESS Prediction.user_predictions 鍏崇郴瀛樺湪: {rel}")
else:
    print("FAILED Prediction.user_predictions 鍏崇郴缂哄け")

# 鍒涘缓涓€涓細璇濆苟娴嬭瘯鍩烘湰鎿嶄綔
Session = sessionmaker(bind=engine)
session = Session()

try:
    # 鍒涘缓涓€涓祴璇曠敤鎴?    test_user = User(
        username='testuser',
        email='test@example.com',
        hashed_password='fakehash',
        status='active'
    )
    session.add(test_user)
    session.commit()
    print(f"SUCCESS 鐢ㄦ埛鍒涘缓鎴愬姛: id={test_user.id}")
    
    # 娓呯悊
    session.query(User).delete()
    session.commit()
    print("SUCCESS 娓呯悊鎴愬姛")
    
except Exception as e:
    print(f"FAILED 鏁版嵁搴撴搷浣滃け璐? {e}")
    session.rollback()

print("\n=== 娴嬭瘯瀹屾垚 ===")
