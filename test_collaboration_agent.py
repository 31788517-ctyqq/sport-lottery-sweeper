#!/usr/bin/env python3
"""
测试协作智能体 API
测试 POST /api/v1/agents/collaboration/analyze 端点功能
"""

import asyncio
import aiohttp
import json
import sys
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API 配置
BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{BASE_URL}/api/v1/agents/collaboration/analyze"

# 测试数据 - 模拟比赛信息
TEST_MATCH_DATA = {
    "match_id": 1,  # 假设的 match_id，实际测试时可能需要调整
    "match_info": "英超联赛：曼联 vs 切尔西，比赛时间：2026-01-31 20:00，地点：老特拉福德",
    "historical_data": "最近5次交锋：曼联2胜1平2负，最近一次交锋：曼联1-1切尔西",
    "current_odds": "胜: 2.10, 平: 3.25, 负: 3.50",
    "market_conditions": "正常市场，流动性良好",
    "available_capital": "50000"
}

# 如果没有提供 match_id，使用默认文本数据
TEST_TEXT_DATA = {
    "match_info": "英超联赛：曼联 vs 切尔西，比赛时间：2026-01-31 20:00，地点：老特拉福德",
    "historical_data": "最近5次交锋：曼联2胜1平2负，最近一次交锋：曼联1-1切尔西",
    "current_odds": "胜: 2.10, 平: 3.25, 负: 3.50",
    "market_conditions": "正常市场，流动性良好",
    "available_capital": "50000"
}

async def test_collaboration_agent(session: aiohttp.ClientSession, test_data: Dict[str, Any]) -> Dict[str, Any]:
    """测试协作智能体 API"""
    try:
        logger.info(f"发送请求到 {API_ENDPOINT}")
        logger.info(f"请求数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
        
        # 注意：实际API可能需要认证，这里使用简单请求
        # 如果API需要认证，需要添加适当的headers
        headers = {
            "Content-Type": "application/json",
            # "Authorization": "Bearer YOUR_TOKEN"  # 如果需要认证
        }
        
        async with session.post(API_ENDPOINT, json=test_data, headers=headers) as response:
            response_text = await response.text()
            logger.info(f"响应状态: {response.status}")
            logger.info(f"响应头: {dict(response.headers)}")
            
            try:
                response_json = json.loads(response_text)
                logger.info(f"响应 JSON: {json.dumps(response_json, indent=2, ensure_ascii=False)}")
                return {
                    "success": response.status == 200,
                    "status": response.status,
                    "data": response_json
                }
            except json.JSONDecodeError:
                logger.warning(f"响应不是有效的 JSON: {response_text[:200]}")
                return {
                    "success": False,
                    "status": response.status,
                    "data": response_text
                }
                
    except aiohttp.ClientError as e:
        logger.error(f"HTTP客户端错误: {e}")
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        logger.error(f"未知错误: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def test_database_integration():
    """测试数据库集成（直接测试智能体类）"""
    try:
        # 导入必要的模块
        import sys
        sys.path.append('backend')
        
        from backend.services.langchain_service import LangChainService
        from backend.services.llm_service import LLMService
        from backend.agents.sequential_collaboration_agent import SequentialCollaborationAgent
        
        logger.info("测试数据库集成...")
        
        # 创建模拟的LLM服务（模拟LLMService接口）
        class MockLLMService:
            def __init__(self):
                self.default_provider = "mock"
                self.providers = {"mock": self}
                
            async def generate_response(self, prompt, provider=None, **kwargs):
                # 返回模拟响应
                return f"模拟响应: {prompt[:50]}..."
            
            def register_provider(self, name, api_key):
                pass
                
            def set_default_provider(self, name):
                self.default_provider = name
        
        # 创建LangChain服务
        llm_service = MockLLMService()
        langchain_service = LangChainService(llm_service)
        
        # 创建协作智能体
        agent = SequentialCollaborationAgent(
            name="test_collaboration_agent",
            description="测试协作智能体",
            langchain_service=langchain_service
        )
        
        # 测试执行（使用文本数据）
        context = TEST_TEXT_DATA.copy()
        result = await agent.execute(context)
        
        logger.info(f"智能体执行结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        return {
            "success": result.get("success", False),
            "result": result
        }
        
    except ImportError as e:
        logger.error(f"导入模块失败: {e}")
        return {
            "success": False,
            "error": f"导入失败: {e}"
        }
    except Exception as e:
        logger.error(f"数据库集成测试失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def main():
    """主测试函数"""
    logger.info("开始测试协作智能体功能")
    
    # 测试1: API端点测试
    logger.info("\n" + "="*50)
    logger.info("测试1: API端点测试")
    logger.info("="*50)
    
    async with aiohttp.ClientSession() as session:
        # 首先测试API是否可访问
        try:
            health_check = f"{BASE_URL}/api/v1/agents/health"
            async with session.get(health_check) as response:
                if response.status == 200:
                    logger.info("智能体健康检查通过")
                else:
                    logger.warning(f"智能体健康检查失败: {response.status}")
        except Exception as e:
            logger.warning(f"无法访问健康检查端点: {e}")
        
        # 测试协作分析API
        api_result = await test_collaboration_agent(session, TEST_TEXT_DATA)
        
        if api_result.get("success"):
            logger.info("✅ API端点测试成功")
        else:
            logger.warning(f"⚠️ API端点测试失败: {api_result.get('error', '未知错误')}")
    
    # 测试2: 数据库集成测试
    logger.info("\n" + "="*50)
    logger.info("测试2: 数据库集成测试")
    logger.info("="*50)
    
    db_result = await test_database_integration()
    
    if db_result.get("success"):
        logger.info("✅ 数据库集成测试成功")
    else:
        logger.warning(f"⚠️ 数据库集成测试失败: {db_result.get('error', '未知错误')}")
    
    # 总结
    logger.info("\n" + "="*50)
    logger.info("测试总结")
    logger.info("="*50)
    
    all_success = api_result.get("success", False) and db_result.get("success", False)
    
    if all_success:
        logger.info("✅ 所有测试通过！协作智能体功能正常")
    else:
        logger.warning("⚠️ 部分测试失败，请检查日志")
        
        # 提供建议
        if not api_result.get("success"):
            logger.info("建议检查:")
            logger.info("1. 确保后端服务正在运行 (端口 8000)")
            logger.info("2. 检查 API 端点路径是否正确")
            logger.info("3. 如果需要认证，请提供有效的 token")
        
        if not db_result.get("success"):
            logger.info("建议检查:")
            logger.info("1. 确保数据库配置正确")
            logger.info("2. 检查模型导入路径")
            logger.info("3. 确认数据库中有测试数据")
    
    return all_success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("测试被用户中断")
        sys.exit(1)
    except Exception as e:
        logger.error(f"测试运行失败: {e}")
        sys.exit(1)