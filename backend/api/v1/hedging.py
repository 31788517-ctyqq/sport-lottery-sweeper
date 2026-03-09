from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import os

# 根据运行环境决定导入路径
try:
    # 当作为包的一部分运行时
    from ...database import get_db
    from ...schemas.hedging import HedgingResult
    from ...services.hedging_service import HedgingService
except ImportError:
    # 当直接运行时
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    from database import get_db
    from schemas.hedging import HedgingResult
    from services.hedging_service import HedgingService

router = APIRouter(prefix="/hedging", tags=["hedging"])


@router.get("/parlay-opportunities", response_model=HedgingResult)
def get_parlay_opportunities(
    date: str,
    db: Session = Depends(get_db)
):
    """
    获取指定日期的二串一组合对冲机会
    筛选利润率大于2%的组合，并确保两场比赛时间间隔超过1小时
    """
    try:
        hedging_service = HedgingService(db)
        result = hedging_service.find_parlay_combinations(date)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对冲机会时发生错误: {str(e)}")


@router.get("/config")
def get_hedging_config(
    db: Session = Depends(get_db)
):
    """
    获取对冲配置
    """
    try:
        hedging_service = HedgingService(db)
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
    investment: float = 1000.0,
    db: Session = Depends(get_db)
):
    """
    手动计算对冲数据
    """
    try:
        hedging_service = HedgingService(db)
        result = hedging_service.calculate_hedging(investment, sp_odd, european_odd)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"计算对冲数据时发生错误: {str(e)}")


@router.get("/mock-data-test")
def get_mock_data_test(
    date: str = "2026-01-27",
    db: Session = Depends(get_db)
):
    """
    获取测试用的模拟数据，用于验证API功能
    """
    try:
        hedging_service = HedgingService(db)
        result = hedging_service._generate_mock_data(date)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取模拟数据时发生错误: {str(e)}")