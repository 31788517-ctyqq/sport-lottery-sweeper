#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试Qwen API配置的脚本
"""

import asyncio
import os
from backend.services.llm_service import LLMService, QwenLLMProvider

async def test_qwen_api():
    """测试Qwen API配置"""
    print("开始测试Qwen API配置...")
    
    # 获取API密钥
    api_key = os.getenv('QWEN_API_KEY')
    if not api_key:
        print("❌ 未找到QWEN_API_KEY环境变量")
        print("请在环境变量或.env文件中配置QWEN_API_KEY")
        return False
    
    print("✅ 找到QWEN_API_KEY")
    
    # 创建Qwen提供商实例
    try:
        monitor = None  # 创建一个简单的监控实例或使用None进行测试
        # 由于QwenLLMProvider构造函数需要monitor参数，我们直接使用LLMService
        llm_service = LLMService()
        llm_service.register_provider('qwen', api_key)
        
        print("✅ Qwen提供商注册成功")
    except Exception as e:
        print(f"❌ Qwen提供商注册失败: {e}")
        return False
    
    # 测试API调用
    try:
        print("\n正在发送测试请求到Qwen API...")
        response = await llm_service.generate_response(
            prompt="你好，请简单介绍一下自己，只需回复一句话。",
            provider="qwen",
            model="qwen-max",
            temperature=0.7
        )
        
        print(f"✅ API调用成功!")
        print(f"响应内容: {response[:100]}{'...' if len(response) > 100 else ''}")
        
        return True
        
    except Exception as e:
        print(f"❌ API调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("Qwen API 配置测试脚本")
    print("=" * 50)
    
    success = asyncio.run(test_qwen_api())
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 Qwen API配置测试通过！")
    else:
        print("❌ Qwen API配置测试失败！")
    print("=" * 50)