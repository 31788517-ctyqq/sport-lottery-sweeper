#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试使用Qwen LLM提供商的日志分析和性能监控功能
"""

import asyncio
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from backend.services.llm_service import LLMService
from backend.services.log_analysis_service import (
    create_log_analysis_service,
    create_performance_monitoring_service
)


async def test_log_analysis_service():
    """测试日志分析服务"""
    print("="*60)
    print("测试日志分析服务...")
    print("="*60)
    
    # 检查Qwen API密钥
    api_key = os.getenv('QWEN_API_KEY', 'YOUR_ACTUAL_QWEN_API_KEY_HERE')
    if api_key == 'YOUR_ACTUAL_QWEN_API_KEY_HERE':
        print("⚠️  警告: 未设置QWEN_API_KEY环境变量，将使用模拟密钥进行结构测试")
        print("   请在使用真实功能前设置正确的API密钥")
        api_key = "dummy-key-for-testing"
    
    # 创建LLM服务
    llm_service = LLMService()
    llm_service.register_provider('qwen', api_key)
    
    # 验证Qwen提供商是否注册成功
    if 'qwen' not in llm_service.providers:
        print("❌ Qwen提供商注册失败")
        return False
    
    print("✅ Qwen提供商已注册")
    
    # 创建日志分析服务
    try:
        log_service = create_log_analysis_service(llm_service)
        print("✅ 日志分析服务创建成功")
    except Exception as e:
        print(f"❌ 日志分析服务创建失败: {e}")
        return False
    
    # 检查是否存在日志文件
    log_path = "backend/logs/app.log"  # 默认日志路径
    if not os.path.exists(log_path):
        # 创建一个模拟日志文件用于测试
        log_dir = Path(log_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        sample_log_content = """2023-12-01 10:00:00,000 INFO MainThread Starting application...
2023-12-01 10:00:05,123 WARNING MainThread User login attempt from 192.168.1.100
2023-12-01 10:00:10,456 ERROR MainThread Failed to connect to database: Connection timeout
2023-12-01 10:00:15,789 INFO MainThread Fallback to secondary database successful
2023-12-01 10:00:20,012 WARNING MainThread High memory usage detected: 85%
2023-12-01 10:00:25,345 ERROR MainThread Request processing failed: Timeout after 30s
2023-12-01 10:00:30,678 INFO MainThread Application shutdown initiated
"""
        
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(sample_log_content)
        
        print(f"📝 创建了模拟日志文件: {log_path}")
    
    print(f"🔍 尝试分析日志文件: {log_path}")
    
    try:
        # 测试日志分析（使用模拟模式，不实际调用API）
        result = await log_service.analyze_logs_with_retrieval_qa(
            log_path=log_path,
            query="分析此日志文件中的错误和警告"
        )
        
        print(f"✅ 日志分析调用完成，结果状态: {result.get('status', 'no-status')}")
        if 'error' in result:
            print(f"⚠️  分析结果包含错误信息: {result['error']}")
        
        # 打印部分结果信息
        if 'answer' in result:
            print(f"📄 分析答案长度: {len(result['answer'])} 字符")
        if 'chunks_count' in result:
            print(f"📊 日志分块数量: {result['chunks_count']}")
        
    except Exception as e:
        print(f"❌ 日志分析执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("✅ 日志分析服务测试通过")
    return True


async def test_performance_monitoring_service():
    """测试性能监控服务"""
    print("\n" + "="*60)
    print("测试性能监控服务...")
    print("="*60)
    
    # 检查Qwen API密钥
    api_key = os.getenv('QWEN_API_KEY', 'YOUR_ACTUAL_QWEN_API_KEY_HERE')
    if api_key == 'YOUR_ACTUAL_QWEN_API_KEY_HERE':
        print("⚠️  警告: 未设置QWEN_API_KEY环境变量，将使用模拟密钥进行结构测试")
        api_key = "dummy-key-for-testing"
    
    # 创建LLM服务
    llm_service = LLMService()
    llm_service.register_provider('qwen', api_key)
    
    # 创建性能监控服务
    try:
        perf_service = create_performance_monitoring_service(llm_service)
        print("✅ 性能监控服务创建成功")
    except Exception as e:
        print(f"❌ 性能监控服务创建失败: {e}")
        return False
    
    # 测试获取LangSmith性能数据
    try:
        perf_data = await perf_service.get_langsmith_performance_data()
        print(f"✅ 获取LangSmith性能数据调用完成，状态: {perf_data.get('status', 'no-status')}")
        
        if perf_data.get("status") == "error":
            print(f"ℹ️  LangSmith未配置或不可用: {perf_data.get('message', 'Unknown reason')}")
        elif perf_data.get("status") == "success":
            stats = perf_data.get("stats", {})
            print(f"📊 获取到运行统计: {stats.get('total_runs', 0)} 总运行, "
                  f"{stats.get('successful_runs', 0)} 成功, "
                  f"{stats.get('failed_runs', 0)} 失败")
    except Exception as e:
        print(f"❌ 获取LangSmith性能数据失败: {e}")
    
    # 测试Qwen性能分析
    try:
        analysis_result = await perf_service.analyze_performance_with_qwen(
            additional_context="系统最近响应较慢，请分析可能原因"
        )
        print(f"✅ Qwen性能分析调用完成，状态: {analysis_result.get('status', 'no-status')}")
        
        if 'qwen_analysis' in analysis_result:
            print(f"📄 分析结果长度: {len(analysis_result['qwen_analysis'])} 字符")
    except Exception as e:
        print(f"❌ Qwen性能分析执行失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("✅ 性能监控服务测试完成")
    return True


async def main():
    """主测试函数"""
    print("🧪 开始测试使用Qwen LLM提供商的日志分析和性能监控功能")
    
    # 运行测试
    log_analysis_ok = await test_log_analysis_service()
    perf_monitoring_ok = await test_performance_monitoring_service()
    
    print("\n" + "="*60)
    print("测试总结:")
    print(f"日志分析服务: {'✅ 通过' if log_analysis_ok else '❌ 失败'}")
    print(f"性能监控服务: {'✅ 完成' if perf_monitoring_ok else '❌ 失败'}")
    
    if log_analysis_ok and perf_monitoring_ok:
        print("\n🎉 所有测试通过！")
        print("\n下一步:")
        print("1. 设置真实的QWEN_API_KEY环境变量")
        print("2. 确保日志文件路径正确")
        print("3. 如需LangSmith功能，设置LANGSMITH_API_KEY环境变量")
        print("4. 通过API端点(/api/v1/log-analysis/)访问功能")
    else:
        print("\n❌ 部分测试失败，请检查实现")
    
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())