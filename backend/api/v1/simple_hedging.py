from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime
import os

# 导入简化的对冲服务
from backend.services.simple_hedging_service import SimpleHedgingService

router = APIRouter(prefix="/simple-hedging", tags=["simple-hedging"])


@router.get("/parlay-opportunities")
def get_parlay_opportunities(
    date: str
):
    """
    获取指定日期的二串一组合对冲机会（使用模拟数据）
    筛选利润率大于2%的组合，并确保两场比赛时间间隔超过1小时
    """
    try:
        hedging_service = SimpleHedgingService()
        result = hedging_service.find_parlay_combinations(date)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对冲机会时发生错误: {str(e)}")


@router.get("/config")
def get_hedging_config():
    """
    获取对冲配置
    """
    try:
        hedging_service = SimpleHedgingService()
        config = hedging_service.config
        return {
            "min_profit_rate": config.min_profit_rate,
            "commission_rate": config.commission_rate,
            "cost_factor": config.cost_factor
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对冲配置时发生错误: {str(e)}")


@router.post("/calculate-manual")
def calculate_manual_hedging(
    sp_odd: float,
    european_odd: float,
    investment: float = 1000.0
):
    """
    手动计算对冲数据
    """
    try:
        hedging_service = SimpleHedgingService()
        result = hedging_service.calculate_hedging(investment, sp_odd, european_odd)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算对冲数据时发生错误: {str(e)}")


@router.get("/mock-data-test")
def get_mock_data_test(
    date: str = "2026-01-27"
):
    """
    获取测试用的模拟数据，用于验证API功能
    """
    try:
        hedging_service = SimpleHedgingService()
        result = hedging_service._generate_mock_data(date)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模拟数据时发生错误: {str(e)}")