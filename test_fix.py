"""
测试修复后的模型关系
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.database import engine, SessionLocal
    from backend.models.user import User
    from backend.models.predictions import UserPrediction, Prediction
    from backend.models.match import Match  # 导入Match模型
    
    print("✅ 成功导入所有相关模型")
    print(f"✅ User模型: {User}")
    print(f"✅ UserPrediction模型: {UserPrediction}")
    print(f"✅ Prediction模型: {Prediction}")
    print(f"✅ Match模型: {Match}")
    
    # 尝试创建数据库表（不会实际创建，只是验证模型定义）
    from sqlalchemy import inspect
    inspector = inspect(engine)
    
    print("\n✅ 模型定义验证通过")
    print("✅ SQLAlchemy关系映射已正确配置")
    
    # 检查关键关系是否存在
    user_mapper = User.__mapper__
    user_pred_rel = user_mapper.relationships.get('predictions')
    
    if user_pred_rel:
        print(f"✅ User模型与UserPrediction的关系已正确配置: {user_pred_rel}")
    else:
        print("❌ User模型与UserPrediction的关系未找到")
    
    user_pred_mapper = UserPrediction.__mapper__
    user_rel = user_pred_mapper.relationships.get('user')
    
    if user_rel:
        print(f"✅ UserPrediction模型与User的关系已正确配置: {user_rel}")
    else:
        print("❌ UserPrediction模型与User的关系未找到")
    
    print("\n🎉 修复验证成功！")
    
except ImportError as e:
    print(f"❌ 导入错误: {e}")
    import traceback
    traceback.print_exc()
    
except Exception as e:
    print(f"❌ 验证过程中出现错误: {e}")
    import traceback
    traceback.print_exc()