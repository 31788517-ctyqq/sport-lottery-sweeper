"""
测试LLM集成是否正常工作
"""
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from backend.main import llm_service
from backend.services.prediction_explainer import PredictionExplainer
from sqlalchemy.orm import Session

def test_llm_service_initialization():
    """测试LLM服务初始化"""
    print("测试LLM服务初始化...")
    
    # 检查是否有注册的提供商
    providers = list(llm_service.providers.keys())
    print(f"注册的提供商: {providers}")
    
    # 检查是否有默认提供商
    print(f"默认提供商: {llm_service.default_provider}")
    
    # 检查成本跟踪
    print(f"累计成本: ${llm_service.request_cost:.4f}")
    
    if providers:
        print("✓ LLM服务初始化成功")
        return True
    else:
        print("! 没有注册任何提供商，请检查API密钥配置")
        return False

def test_basic_llm_functionality():
    """测试基本LLM功能"""
    print("\n测试基本LLM功能...")
    
    if not llm_service.providers:
        print("! 没有可用的提供商，跳过功能测试")
        return False
    
    try:
        # 使用默认提供商进行简单测试
        response = llm_service.generate_response(
            "你好，请简单介绍一下自己。",
            max_tokens=50
        )
        print(f"LLM响应: {response[:100]}...")  # 只显示前100个字符
        print("✓ 基本LLM功能测试成功")
        return True
    except Exception as e:
        print(f"! 基本LLM功能测试失败: {e}")
        return False

def test_prediction_explainer():
    """测试预测解释器"""
    print("\n测试预测解释器...")
    
    if not llm_service.providers:
        print("! 没有可用的提供商，跳过预测解释器测试")
        return False
    
    try:
        # 创建一个模拟的数据库会话和预测结果
        # 由于我们没有实际的数据库连接，这里仅测试类的初始化
        class MockDBSession:
            pass
        
        mock_db = MockDBSession()
        explainer = PredictionExplainer(mock_db, llm_service)
        
        # 模拟预测结果
        mock_prediction = {
            "probabilities": {
                "home_win": 0.4,
                "draw": 0.3,
                "away_win": 0.3
            },
            "confidence": 0.75
        }
        
        print("✓ 预测解释器初始化成功")
        return True
    except Exception as e:
        print(f"! 预测解释器测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试LLM集成...")
    print("="*50)
    
    results = []
    results.append(test_llm_service_initialization())
    results.append(test_basic_llm_functionality())
    results.append(test_prediction_explainer())
    
    print("\n" + "="*50)
    print("测试总结:")
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    
    if passed > 0:
        print("✓ 部分或全部测试通过")
    else:
        print("✗ 所有测试失败")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)