from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import numpy as np
from ....database import get_db
from ....services.lightweight_inference_service import LightweightInferenceService

router = APIRouter(prefix="/real-time", tags=["real-time"])


@router.post("/decision")
async def get_real_time_decision(
    payload: Dict[str, Any],
    db: Session = Depends(get_db)
):
    """获取实时决策"""
    try:
        # 使用轻量级推理服务快速处理
        inference_service = LightweightInferenceService()
        
        # 准备输入数据
        input_data = prepare_input_for_quick_model(payload)
        result = inference_service.predict(input_data)
        
        # 返回决策结果
        return {
            "decision": map_result_to_decision(result),
            "confidence": float(np.max(result)),
            "execution_time": "low_latency",
            "model_used": "lightweight"
        }
    except Exception as e:
        # 如果轻量级模型失败，回退到完整模型
        try:
            from ....main import llm_service
            fallback_result = llm_service.generate_response(
                f"基于以下数据提供快速决策建议：{payload}",
                provider="qwen"
            )
            return {
                "decision": fallback_result, 
                "confidence": 0.5, 
                "execution_time": "normal",
                "model_used": "llm_fallback",
                "error": str(e)
            }
        except Exception as llm_error:
            # 如果LLM服务也不可用，返回错误
            raise HTTPException(
                status_code=500, 
                detail=f"所有决策服务都不可用 - 轻量级模型错误: {str(e)}, LLM错误: {str(llm_error)}"
            )


def prepare_input_for_quick_model(data: Dict[str, Any]) -> np.ndarray:
    """准备轻量级模型输入"""
    # 这里需要根据实际模型输入要求进行数据转换
    # 示例：将赔率数据转换为数值数组
    features = []
    
    # 提取赔率数据
    home_win_odd = data.get('home_win_odd', 2.0)
    draw_odd = data.get('draw_odd', 3.0)
    away_win_odd = data.get('away_win_odd', 3.5)
    
    # 提取其他特征
    home_team_rank = data.get('home_team_rank', 10)
    away_team_rank = data.get('away_team_rank', 10)
    historical_win_rate = data.get('historical_win_rate', 0.33)
    
    # 组织为特征向量
    features = [
        home_win_odd,
        draw_odd,
        away_win_odd,
        home_team_rank,
        away_team_rank,
        historical_win_rate
    ]
    
    return np.array(features)


def map_result_to_decision(result: np.ndarray) -> str:
    """将模型结果映射到决策"""
    # 假设模型输出为[主胜概率, 平局概率, 客胜概率]
    if len(result.shape) > 1:
        probabilities = result[0]  # 取第一个样本的结果
    else:
        probabilities = result
    
    # 确定最高概率的选项
    max_idx = np.argmax(probabilities)
    
    decisions = ["home_win", "draw", "away_win"]
    return decisions[max_idx]