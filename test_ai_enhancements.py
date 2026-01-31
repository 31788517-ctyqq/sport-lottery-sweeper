"""
AI增强功能集成测试
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.agents.odds_monitor_agent import OddsMonitorAgent
from backend.services.hedge_service import HedgeService
from backend.agents.base_agent import BaseAgent
from backend.services.user_profile_service import UserProfileService
from backend.agents.recommendation_agent import RecommendationAgent
from backend.services.lightweight_inference_service import LightweightInferenceService
from backend.agents.communication_protocol import CommunicationHub, Message, MessageType
from backend.agents.collaborative_prediction_agent import (
    DataCollectionAgent, 
    AnalysisAgent, 
    PredictionAgent, 
    RiskControlAgent
)


def test_base_agent_abstract():
    """测试BaseAgent是否正确实现抽象基类"""
    with pytest.raises(TypeError):
        BaseAgent("test", {})


@pytest.mark.asyncio
async def test_odds_monitor_agent():
    """测试赔率监控智能体"""
    # 模拟hedge_service
    hedge_service = AsyncMock(spec=HedgeService)
    hedge_service.process_opportunities = AsyncMock(return_value=[{"status": "processed"}])
    
    agent_config = {
        "interval": 5, 
        "threshold": 0.02
    }
    agent = OddsMonitorAgent("test_agent", agent_config, hedge_service)
    
    # Mock agent的方法
    agent.fetch_latest_odds = AsyncMock(return_value=[])
    agent.find_arbitrage_opportunities = MagicMock(return_value=[])
    
    context = {}
    result = await agent.execute(context)
    
    assert result is not None
    assert "status" in result


def test_user_profile_service():
    """测试用户画像服务"""
    # 模拟数据库会话
    mock_db = MagicMock()
    
    # 模拟查询结果
    mock_record = MagicMock()
    mock_record.user_id = 1
    mock_record.amount = 50
    mock_record.bet_type = "win"
    mock_record.is_winning = True
    
    mock_db.query.return_value.filter.return_value.all.return_value = [mock_record]
    
    service = UserProfileService(mock_db)
    profile = service.build_profile(1)
    
    assert "risk_tolerance" in profile
    assert "preferred_teams" in profile
    assert "betting_patterns" in profile
    assert "success_rate" in profile


@pytest.mark.asyncio
async def test_recommendation_agent():
    """测试推荐智能体"""
    # 模拟服务
    mock_user_profile_service = MagicMock()
    mock_user_profile_service.build_profile.return_value = {
        "risk_tolerance": 0.5,
        "preferred_teams": ["Team A"],
        "betting_patterns": {"avg_bet_amount": 50},
        "success_rate": 0.6
    }
    
    mock_prediction_service = MagicMock()
    
    agent = RecommendationAgent(
        "test_rec_agent", 
        {}, 
        mock_user_profile_service, 
        mock_prediction_service
    )
    
    # 准备测试数据
    mock_match = {
        "id": 1,
        "home_team": "Team A",
        "away_team": "Team B",
        "prediction": {"confidence": 0.8}
    }
    
    context = {
        "user_id": 1,
        "upcoming_matches": [mock_match]
    }
    
    result = await agent.execute(context)
    
    assert "user_id" in result
    assert "recommendations" in result
    assert result["user_id"] == 1


def test_lightweight_inference_service():
    """测试轻量级推理服务"""
    service = LightweightInferenceService()
    
    # 测试预测功能
    import numpy as np
    test_input = np.array([2.0, 3.0, 2.5, 5, 7, 0.33])
    result = service.predict(test_input)
    
    assert result is not None
    assert isinstance(result, np.ndarray)
    assert result.shape[1] == 3  # 三分类问题


@pytest.mark.asyncio
async def test_communication_hub():
    """测试通信中心"""
    hub = CommunicationHub()
    
    # 创建一个简单的回调函数来接收消息
    received_messages = []
    
    async def message_handler(message):
        received_messages.append(message)
    
    # 注册一个虚拟智能体
    hub.register_agent("test_agent", message_handler)
    
    # 发送一条消息
    test_message = Message(
        MessageType.REQUEST,
        "sender",
        "test_agent",
        {"test": "data"}
    )
    
    await hub.send_message(test_message)
    
    # 验证消息是否被接收
    assert len(received_messages) == 1
    assert received_messages[0].content["test"] == "data"


@pytest.mark.asyncio
async def test_collaborative_agents():
    """测试协作智能体"""
    # 创建通信中心
    hub = CommunicationHub()
    
    # 创建智能体
    data_agent = DataCollectionAgent("data_collection_agent", {}, hub)
    analysis_agent = AnalysisAgent("analysis_agent", {}, hub)
    prediction_agent = PredictionAgent("prediction_agent", {}, hub)
    risk_agent = RiskControlAgent("risk_control_agent", {}, hub)
    
    # 验证所有智能体都被注册
    status = await hub.get_agent_status()
    assert "data_collection_agent" in status
    assert "analysis_agent" in status
    assert "prediction_agent" in status
    assert "risk_control_agent" in status


def main():
    """运行所有测试"""
    print("开始运行AI增强功能集成测试...")
    
    # 由于部分测试使用了asyncio，我们单独运行它们
    test_base_agent_abstract()
    print("✓ BaseAgent抽象测试通过")
    
    # 运行异步测试
    asyncio.run(test_odds_monitor_agent())
    print("✓ 赔率监控智能体测试通过")
    
    test_user_profile_service()
    print("✓ 用户画像服务测试通过")
    
    asyncio.run(test_recommendation_agent())
    print("✓ 推荐智能体测试通过")
    
    test_lightweight_inference_service()
    print("✓ 轻量级推理服务测试通过")
    
    asyncio.run(test_communication_hub())
    print("✓ 通信中心测试通过")
    
    asyncio.run(test_collaborative_agents())
    print("✓ 协作智能体测试通过")
    
    print("\n所有AI增强功能测试通过！")


if __name__ == "__main__":
    main()