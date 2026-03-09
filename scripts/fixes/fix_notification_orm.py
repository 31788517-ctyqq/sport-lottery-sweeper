import sys
sys.path.insert(0, 'backend')

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.user import User
import json

engine = create_engine('sqlite:///sport_lottery.db')
Session = sessionmaker(bind=engine)
session = Session()

try:
    user = session.query(User).filter(User.username == 'admin').first()
    if user:
        print(f"找到用户: {user.username}")
        print(f"当前notification_preferences值: {user.notification_preferences}")
        print(f"类型: {type(user.notification_preferences)}")
        
        # 如果是字符串，转换为字典
        if isinstance(user.notification_preferences, str):
            try:
                parsed = json.loads(user.notification_preferences) if user.notification_preferences.strip() else {}
                print(f"解析为字典: {parsed}")
                # 直接赋值字典
                user.notification_preferences = parsed
                session.commit()
                print("已更新为字典")
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                user.notification_preferences = {}
                session.commit()
                print("已设置为空字典")
        else:
            print("已经是字典或非字符串类型")
    else:
        print("未找到admin用户")
except Exception as e:
    session.rollback()
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    session.close()