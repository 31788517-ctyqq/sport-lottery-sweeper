from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import numpy as np
import time
from datetime import datetime
from ...database import get_db
from ...services.enhanced_inference_service import get_enhanced_inference_service, ModelType
from ...optimization.query_optimization_integration import optimize_database_query, monitor_query_performance
from ...monitoring.business_metrics import record_decision_metric

router = APIRouter(prefix="/real-time", tags=["real-time"])


@router.post("/decision")
@optimize_database_query(use_cache=True, cache_key_prefix="decision")
async def get_real_time_decision(
    payload: Dict[str, Any] = Body(...),
    model_version: Optional[str] = None,
    use_cache: bool = True,
    db: Session = Depends(get_db)
):
    """获取实时决策（增强版）"""
    start_time = time.time()
    decision_id = f"decision_{int(time.time() * 1000)}_{hash(str(payload)) % 10000}"
    
    try:
        # 获取增强推理服务
        inference_service = get_enhanced_inference_service()
        
        # 准备输入数据
        input_data = prepare_input_for_enhanced_model(payload)
        
        # 执行推理
        result = inference_service.predict(
            input_data=input_data,
            model_version=model_version
        )
        
        # 记录决策指标
        latency = time.time() - start_time
        record_decision_metric(
            decision_id=decision_id,
            correct=None,  # 实际应用中可以根据结果验证来设置
            confidence=result.get('confidence', 0.0),
            latency=latency
        )
        
        # 返回决策结果
        return {
            "success": True,
            "data": {
                "decision": result.get('decision', 'draw'),
                "confidence": result.get('confidence', 0.0),
                "probabilities": result.get('probabilities', {}),
                "model_version": result.get('model_version', 'unknown'),
                "model_type": result.get('model_type', 'unknown'),
                "execution_time_ms": round(latency * 1000, 2),
                "decision_id": decision_id,
                "timestamp": datetime.now().isoformat(),
                "features_used": result.get('features_used', [])
            },
            "message": "决策生成成功"
        }
        
    except Exception as e:
        # 如果增强模型失败，回退到轻量级模型
        fallback_result = fallback_to_lightweight_model(payload)
        
        # 记录错误
        latency = time.time() - start_time
        record_decision_metric(
            decision_id=decision_id,
            correct=False,
            confidence=fallback_result.get('confidence', 0.0),
            latency=latency
        )
        
        return {
            "success": True,
            "data": {
                **fallback_result,
                "execution_time_ms": round(latency * 1000, 2),
                "decision_id": decision_id,
                "timestamp": datetime.now().isoformat(),
                "fallback": True,
                "error": str(e)
            },
            "message": "使用备用模型生成决策"
        }


@router.post("/decision/batch")
async def get_batch_decisions(
    payloads: List[Dict[str, Any]] = Body(...),
    model_version: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """批量获取实时决策"""
    try:
        inference_service = get_enhanced_inference_service()
        
        # 批量推理
        results = inference_service.batch_predict(payloads)
        
        return {
            "success": True,
            "data": {
                "decisions": results,
                "total": len(results),
                "avg_confidence": np.mean([r.get('confidence', 0) for r in results]) if results else 0,
                "timestamp": datetime.now().isoformat()
            },
            "message": f"批量决策生成成功，共{len(results)}条"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"批量决策失败: {str(e)}"
        )


@router.post("/decision/train")
async def train_decision_model(
    training_data: List[Dict[str, Any]] = Body(...),
    labels: List[int] = Body(...),
    model_type: ModelType = Body(ModelType.RANDOM_FOREST),
    validation_split: float = Body(0.2),
    db: Session = Depends(get_db)
):
    """训练新的决策模型"""
    try:
        inference_service = get_enhanced_inference_service()
        
        # 转换数据格式
        X = np.array([prepare_input_for_enhanced_model(data) for data in training_data])
        y = np.array(labels)
        
        # 训练模型
        result = inference_service.train_model(
            training_data=X,
            labels=y,
            model_type=model_type,
            validation_split=validation_split
        )
        
        return {
            "success": True,
            "data": result,
            "message": "模型训练成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"模型训练失败: {str(e)}"
        )


@router.get("/decision/models")
async def get_available_models():
    """获取可用模型列表"""
    try:
        inference_service = get_enhanced_inference_service()
        models = inference_service.get_available_model_versions()
        
        return {
            "success": True,
            "data": {
                "models": models,
                "active_model": inference_service.active_model_version.to_dict() 
                    if inference_service.active_model_version else None,
                "total_models": len(models)
            },
            "message": "获取模型列表成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取模型列表失败: {str(e)}"
        )


def prepare_input_for_enhanced_model(data: Dict[str, Any]) -> np.ndarray:
    """准备增强模型输入"""
    # 提取标准特征
    features = []
    
    # 基础赔率特征
    features.append(data.get('home_win_odd', 2.0))
    features.append(data.get('draw_odd', 3.0))
    features.append(data.get('away_win_odd', 3.5))
    
    # 球队特征
    features.append(data.get('home_team_rank', 10))
    features.append(data.get('away_team_rank', 10))
    features.append(data.get('historical_win_rate', 0.33))
    
    # 扩展特征（如果提供）
    features.append(data.get('home_form', 0.5))
    features.append(data.get('away_form', 0.5))
    features.append(data.get('injury_impact', 0.0))
    features.append(data.get('motivation_factor', 0.5))
    
    # 填充或截断到标准特征数
    standard_features = 10
    if len(features) > standard_features:
        features = features[:standard_features]
    else:
        features.extend([0.0] * (standard_features - len(features)))
    
    return np.array(features)


def fallback_to_lightweight_model(payload: Dict[str, Any]) -> Dict[str, Any]:
    """回退到轻量级模型"""
    try:
        from ....services.lightweight_inference_service import LightweightInferenceService
        service = LightweightInferenceService()
        
        # 简化特征提取
        features = [
            payload.get('home_win_odd', 2.0),
            payload.get('draw_odd', 3.0),
            payload.get('away_win_odd', 3.5),
            payload.get('home_team_rank', 10),
            payload.get('away_team_rank', 10),
            payload.get('historical_win_rate', 0.33)
        ]
        
        input_data = np.array(features).reshape(1, -1)
        result = service.predict(input_data)
        
        # 映射到决策
        probabilities = result[0] if len(result.shape) > 1 else result
        max_idx = np.argmax(probabilities)
        decisions = ["home_win", "draw", "away_win"]
        
        return {
            'decision': decisions[max_idx],
            'confidence': float(probabilities[max_idx]),
            'probabilities': {
                'home_win': float(probabilities[0]),
                'draw': float(probabilities[1]),
                'away_win': float(probabilities[2])
            },
            'model_version': 'lightweight_fallback',
            'model_type': 'logistic_regression',
            'features_used': ['home_win_odd', 'draw_odd', 'away_win_odd', 
                           'home_team_rank', 'away_team_rank', 'historical_win_rate']
        }
        
    except Exception as e:
        # 最终回退：均匀分布
        return {
            'decision': 'draw',
            'confidence': 0.33,
            'probabilities': {
                'home_win': 0.33,
                'draw': 0.34,
                'away_win': 0.33
            },
            'model_version': 'uniform_fallback',
            'model_type': 'fallback',
            'features_used': [],
            'error': str(e)
        }


@router.get("/decision/performance")
async def get_model_performance():
    """获取模型性能历史"""
    try:
        inference_service = get_enhanced_inference_service()
        performance_history = inference_service.get_model_performance_history()
        
        return {
            "success": True,
            "data": {
                "performance_history": performance_history,
                "total_records": len(performance_history)
            },
            "message": "获取性能历史成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取性能历史失败: {str(e)}"
        )