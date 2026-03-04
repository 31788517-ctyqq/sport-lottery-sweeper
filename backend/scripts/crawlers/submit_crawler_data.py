"""
爬虫数据提交脚本
用于将爬取到的数据提交到审核系统
"""
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .database import SessionLocal
from .models.data_review import DataTypeEnum


async def submit_match_schedule_data(data: List[Dict[str, Any]], external_source: str = "crawler"):
    """
    提交比赛赛程数据到审核系统
    """
    url = "http://localhost:8000/api/v1/submission/submit-data"
    
    for match_data in data:
        payload = {
            "data_type": DataTypeEnum.MATCH_SCHEDULE.value,
            "original_data": match_data,
            "external_source": external_source,
            "external_id": match_data.get("external_id") or f"match_{match_data.get('id', '')}"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    print(f"✓ 比赛数据提交成功: {match_data.get('home_team', 'Unknown')} vs {match_data.get('away_team', 'Unknown')}")
                else:
                    print(f"✗ 比赛数据提交失败: {response.text}")
            except Exception as e:
                print(f"✗ 比赛数据提交异常: {str(e)}")


async def submit_prediction_data(data: List[Dict[str, Any]], external_source: str = "prediction_model"):
    """
    提交预测数据到审核系统
    """
    url = "http://localhost:8000/api/v1/submission/submit-data"
    
    for pred_data in data:
        payload = {
            "data_type": DataTypeEnum.PREDICTION.value,
            "original_data": pred_data,
            "external_source": external_source,
            "external_id": pred_data.get("external_id") or f"pred_{pred_data.get('id', '')}"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    print(f"✓ 预测数据提交成功: {pred_data.get('match_id', 'Unknown')}")
                else:
                    print(f"✗ 预测数据提交失败: {response.text}")
            except Exception as e:
                print(f"✗ 预测数据提交异常: {str(e)}")


async def submit_intelligence_data(data: List[Dict[str, Any]], external_source: str = "intelligence_feed"):
    """
    提交情报数据到审核系统
    """
    url = "http://localhost:8000/api/v1/submission/submit-data"
    
    for intel_data in data:
        payload = {
            "data_type": DataTypeEnum.INTELLIGENCE.value,
            "original_data": intel_data,
            "external_source": external_source,
            "external_id": intel_data.get("external_id") or f"intel_{intel_data.get('id', '')}"
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, json=payload)
                if response.status_code == 200:
                    print(f"✓ 情报数据提交成功: {intel_data.get('title', 'Unknown')}")
                else:
                    print(f"✗ 情报数据提交失败: {response.text}")
            except Exception as e:
                print(f"✗ 情报数据提交异常: {str(e)}")


async def simulate_crawler_data_flow():
    """
    模拟爬虫数据流：爬取数据 -> 提交审核 -> 等待批准 -> 发布
    """
    print("🚀 开始模拟爬虫数据提交流程...")
    
    # 模拟爬取到的比赛数据
    match_data = [
        {
            "id": 1,
            "match_number": "20260117001",
            "home_team": "巴塞罗那",
            "away_team": "皇家马德里",
            "league": "西甲",
            "match_date": "2026-01-17",
            "match_time": "20:00",
            "venue": "诺坎普球场",
            "odds": {
                "home_win": 2.10,
                "draw": 3.20,
                "away_win": 3.50
            },
            "importance": "high",
            "external_id": "match_20260117001"
        },
        {
            "id": 2,
            "match_number": "20260117002",
            "home_team": "拜仁慕尼黑",
            "away_team": "多特蒙德",
            "league": "德甲",
            "match_date": "2026-01-17",
            "match_time": "21:00",
            "venue": "安联球场",
            "odds": {
                "home_win": 1.80,
                "draw": 3.60,
                "away_win": 4.20
            },
            "importance": "high",
            "external_id": "match_20260117002"
        }
    ]
    
    # 模拟预测数据
    prediction_data = [
        {
            "id": 1,
            "match_id": 1,
            "predicted_winner": "home",
            "confidence": 0.75,
            "predicted_score": "2:1",
            "method": "machine_learning",
            "analysis": "基于历史数据和球队状态分析...",
            "external_id": "pred_001"
        },
        {
            "id": 2,
            "match_id": 2,
            "predicted_winner": "home",
            "confidence": 0.68,
            "predicted_score": "3:0",
            "method": "statistical_model",
            "analysis": "拜仁主场优势明显...",
            "external_id": "pred_002"
        }
    ]
    
    # 模拟情报数据
    intelligence_data = [
        {
            "id": 1,
            "match_id": 1,
            "type": "injury",
            "title": "皇马主力前锋受伤",
            "content": "皇家马德里的主力前锋在训练中受伤，可能无法参加本场比赛。",
            "weight": 8.5,
            "source": "official",
            "time": "2026-01-16 18:30",
            "impact": 8.5,
            "external_id": "intel_001"
        },
        {
            "id": 2,
            "match_id": 2,
            "type": "weather",
            "title": "比赛当日有雨",
            "content": "气象预报显示比赛当天气温较低且有雨，可能影响球员发挥。",
            "weight": 5.0,
            "source": "weather_service",
            "time": "2026-01-17 08:00",
            "impact": 5.0,
            "external_id": "intel_002"
        }
    ]
    
    print("\n📊 提交比赛赛程数据...")
    await submit_match_schedule_data(match_data)
    
    print("\n🔮 提交预测数据...")
    await submit_prediction_data(prediction_data)
    
    print("\n🕵️ 提交情报数据...")
    await submit_intelligence_data(intelligence_data)
    
    print("\n✅ 所有数据已提交到审核系统，等待管理员审核确认后发布")


if __name__ == "__main__":
    asyncio.run(simulate_crawler_data_flow())