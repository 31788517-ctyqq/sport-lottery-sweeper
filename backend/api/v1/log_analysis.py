"""
日志分析和性能监控API端点
使用Qwen LLM提供商
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import logging

from ...database import get_db
from ...services.llm_service import LLMService
from ...services.log_analysis_service import (
    create_log_analysis_service, 
    create_performance_monitoring_service,
    LogAnalysisService, 
    PerformanceMonitoringService
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/log-analysis", tags=["log-analysis"])

# 从主应用获取LLM服务实例
def _get_llm_service():
    svc = None
    try:
        from ... import main as main_module
        svc = getattr(main_module, "llm_service", None)
    except Exception:
        svc = None
    if not svc:
        try:
            import __main__ as main_module
            svc = getattr(main_module, "llm_service", None)
        except Exception:
            svc = None
    return svc


@router.post("/analyze-logs")
async def analyze_system_logs(
    log_path: str = Query(..., description="日志文件的路径"),
    query: Optional[str] = Query(None, description="针对日志的特定查询"),
    db: Session = Depends(get_db)
):
    """使用RetrievalQA分析系统日志"""
    try:
        llm_service = _get_llm_service()
        if not llm_service or 'qwen' not in llm_service.providers:
            raise HTTPException(status_code=503, detail="Qwen提供商未配置")
        
        log_service = create_log_analysis_service(llm_service)
        result = await log_service.analyze_logs_with_retrieval_qa(log_path, query)
        
        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"日志分析API调用失败: {e}")
        raise HTTPException(status_code=500, detail=f"日志分析失败: {str(e)}")


@router.get("/performance-data")
async def get_performance_data():
    """获取LangSmith性能数据"""
    try:
        llm_service = _get_llm_service()
        if not llm_service or 'qwen' not in llm_service.providers:
            raise HTTPException(status_code=503, detail="Qwen提供商未配置")
        
        perf_service = create_performance_monitoring_service(llm_service)
        result = await perf_service.get_langsmith_performance_data()
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取性能数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取性能数据失败: {str(e)}")


@router.post("/analyze-performance")
async def analyze_performance(
    additional_context: Optional[str] = Query(None, description="附加的上下文信息"),
    db: Session = Depends(get_db)
):
    """使用Qwen分析性能数据"""
    try:
        llm_service = _get_llm_service()
        if not llm_service or 'qwen' not in llm_service.providers:
            raise HTTPException(status_code=503, detail="Qwen提供商未配置")
        
        perf_service = create_performance_monitoring_service(llm_service)
        result = await perf_service.analyze_performance_with_qwen(additional_context or "")
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"性能分析API调用失败: {e}")
        raise HTTPException(status_code=500, detail=f"性能分析失败: {str(e)}")


@router.get("/capabilities")
async def get_log_analysis_capabilities():
    """获取日志分析功能的能力信息"""
    capabilities = {
        "features": [
            "使用RetrievalQA进行日志内容分析",
            "使用Qwen LLM进行智能分析",
            "LangSmith性能数据监控",
            "Qwen驱动的性能趋势分析"
        ],
        "requirements": [
            "Qwen API密钥配置",
            "日志文件路径可访问",
            "LangSmith API密钥（可选）"
        ],
        "endpoints": {
            "/analyze-logs": "分析指定路径的日志文件",
            "/performance-data": "获取LangSmith性能数据",
            "/analyze-performance": "使用Qwen分析性能数据",
            "/capabilities": "获取功能能力信息"
        }
    }
    
    return capabilities
