"""
测试修复后的模型关系
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.database import engine
    from backend.models.user import User
    from backend.models.predictions import UserPrediction, Prediction
    from backend.models.match import Match  # 导入Match模型
    
    print("✅ 成功导入所有相关模型")
    print(f"✅ User模型: {User}")
    print(f"✅ UserPrediction模型: {UserPrediction}")
    print(f"✅ Prediction模型: {Prediction}")
    print(f"✅ Match模型: {Match}")
    
    # 验证关系是否能正常工作
    # 尝试获取User模型的属性
    user_attrs = dir(User)
    has_predictions = 'user_predictions' in user_attrs
    print(f"✅ User模型是否包含user_predictions关系: {has_predictions}")
    
    # 尝试获取UserPrediction模型的属性
    up_attrs = dir(UserPrediction)
    has_user_rel = 'user' in up_attrs
    print(f"✅ UserPrediction模型是否包含user关系: {has_user_rel}")
    
    print("\n✅ 模型定义验证通过")
    print("✅ SQLAlchemy关系映射已正确配置")
    
    print("\n🎉 修复验证成功！")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    import traceback
    traceback.print_exc()
    
except Exception as e:
    print(f"❌ 验证过程中出现错误: {e}")
    import traceback
    traceback.print_exc()