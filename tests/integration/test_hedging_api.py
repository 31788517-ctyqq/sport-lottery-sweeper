"""
对冲管理API测试脚本
用于验证对冲管理模块的API是否正常工作
"""

import sys
import os
from datetime import datetime

# 添加项目根目录和backend目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'backend'))

def test_hedging_api():
    """
    测试对冲API功能
    """
    try:
        # 导入必要的模块
        from backend.database import SessionLocal
        from backend.services.hedging_service import HedgingService
        
        # 创建数据库会话
        db = SessionLocal()
        
        try:
            # 创建对冲服务实例
            hedging_service = HedgingService(db)
            
            # 测试获取默认配置
            config = hedging_service.config
            print(f"对冲配置: 最低利润率={config.min_profit_rate}, 佣金率={config.commission_rate}, 成本因子={config.cost_factor}")
            
            # 测试计算函数
            result = hedging_service.calculate_hedging(1000, 3.6, 5.0)
            print(f"对冲计算示例: 投入={result['investment']:.2f}, 收益={result['revenue']:.2f}, 利润={result['profit']:.2f}, 利润率={result['profit_rate']*100:.2f}%, 是否盈利={result['is_profitable']}")
            
            # 测试获取模拟数据
            today = datetime.now().strftime("%Y-%m-%d")
            mock_result = hedging_service._generate_mock_data(today)
            print(f"模拟数据测试: 日期={mock_result.date}, 发现机会={mock_result.total_count}个")
            
            if mock_result.opportunities:
                first_opportunity = mock_result.opportunities[0]
                print(f"首个机会: {first_opportunity.match1_home_team} VS {first_opportunity.match1_away_team} "
                      f"和 {first_opportunity.match2_home_team} VS {first_opportunity.match2_away_team}, "
                      f"利润={first_opportunity.profit_amount:.2f}, 利润率={first_opportunity.profit_rate*100:.2f}%")
            
        finally:
            db.close()
            
        print("[OK] 对冲API测试成功!")
        return True
        
    except ImportError as e:
        print(f"[ERROR] 导入模块失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"[ERROR] 对冲API测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("[TEST] 开始测试对冲管理API...")
    success = test_hedging_api()
    
    if success:
        print("\n[SUCCESS] 对冲管理模块已成功配置并可以使用模拟数据运行!")
        print("\n[LOG] 接下来可以:")
        print("- 启动后端服务器 (uvicorn backend.main:app --reload)")
        print("- 访问前端管理界面并测试对冲管理功能")
        print("- 在前端中查看模拟的对冲机会数据")
    else:
        print("\n[ERROR] 测试失败，请检查配置和依赖项")