#!/usr/bin/env python3
"""
插入示例AI服务日志记录到log_entries表
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timezone
import json

# 数据库连接
db_path = os.path.join(os.path.dirname(__file__), 'data/sport_lottery.db')
engine = create_engine(f'sqlite:///{db_path}')
Session = sessionmaker(bind=engine)
db = Session()

# 创建示例AI日志记录
sample_logs = [
    {
        "timestamp": datetime.now(timezone.utc),
        "level": "INFO",
        "module": "ai",
        "message": "AI服务调用成功: 用户 'admin' 请求平局预测分析",
        "user_id": None,
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0",
        "session_id": "session_123",
        "request_path": "/api/v1/llm/chat",
        "response_status": 200,
        "duration_ms": 1250,
        "extra_data": json.dumps({
            "user_id": "admin",
            "provider": "zhipuai",
            "model": "glm-4",
            "input_tokens": 256,
            "output_tokens": 128,
            "success": True
        })
    },
    {
        "timestamp": datetime.now(timezone.utc),
        "level": "INFO",
        "module": "llm",
        "message": "LLM响应生成: 智谱AI提供商返回了预测结果",
        "user_id": None,
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0",
        "session_id": "session_123",
        "request_path": "/api/v1/llm/chat",
        "response_status": 200,
        "duration_ms": 890,
        "extra_data": json.dumps({
            "provider": "zhipuai",
            "response_time_ms": 890,
            "model": "glm-4",
            "temperature": 0.7
        })
    },
    {
        "timestamp": datetime.now(timezone.utc),
        "level": "WARN",
        "module": "ai",
        "message": "AI服务调用延迟: 用户 'user1' 请求超过3秒",
        "user_id": None,
        "ip_address": "192.168.1.101",
        "user_agent": "PostmanRuntime/7.36",
        "session_id": "session_456",
        "request_path": "/api/v1/llm/chat",
        "response_status": 200,
        "duration_ms": 3120,
        "extra_data": json.dumps({
            "user_id": "user1",
            "provider": "qwen",
            "duration_ms": 3120,
            "threshold_ms": 3000,
            "warning": "high_latency"
        })
    },
    {
        "timestamp": datetime.now(timezone.utc),
        "level": "ERROR",
        "module": "llm",
        "message": "AI服务调用失败: 智谱AI提供商返回认证错误",
        "user_id": None,
        "ip_address": "192.168.1.102",
        "user_agent": "curl/7.88",
        "session_id": "session_789",
        "request_path": "/api/v1/llm/chat",
        "response_status": 401,
        "duration_ms": 450,
        "extra_data": json.dumps({
            "provider": "zhipuai",
            "error_code": "AUTH_FAILED",
            "error_message": "Invalid API key",
            "success": False
        })
    },
    {
        "timestamp": datetime.now(timezone.utc),
        "level": "INFO",
        "module": "conversation_agent",
        "message": "对话助手处理完成: 用户 'guest' 的查询已成功响应",
        "user_id": None,
        "ip_address": "192.168.1.103",
        "user_agent": "Python/3.11",
        "session_id": "session_abc",
        "request_path": "/api/v1/llm/chat",
        "response_status": 200,
        "duration_ms": 760,
        "extra_data": json.dumps({
            "user_id": "guest",
            "query_type": "odds_inquiry",
            "response_length": 245,
            "processing_time_ms": 760
        })
    }
]

# 导入模型
from backend.models.log_entry import LogEntry

# 插入记录
for log_data in sample_logs:
    log_entry = LogEntry(**log_data)
    db.add(log_entry)

db.commit()
print(f"成功插入 {len(sample_logs)} 条AI服务日志记录")

# 验证插入
count = db.query(LogEntry).filter(
    LogEntry.module.ilike('%ai%') | LogEntry.module.ilike('%llm%')
).count()
print(f"当前AI相关日志总数: {count}")

db.close()