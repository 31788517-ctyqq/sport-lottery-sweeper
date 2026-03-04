#!/usr/bin/env python3
"""
测试LLM供应商模块导入
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from backend.api.v1 import llm_providers
    print("✅ llm_providers 模块导入成功")
    print(f"   路由器对象: {llm_providers.router}")
    print(f"   路由数量: {len(llm_providers.router.routes)}")
    
    # 检查导入的类
    from backend.schemas.llm_provider import LLMProviderTestRequest, LLMProviderBatchRequest
    print("✅ LLMProviderTestRequest 导入成功")
    print("✅ LLMProviderBatchRequest 导入成功")
    
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"❌ 其他错误: {e}")
    import traceback
    traceback.print_exc()