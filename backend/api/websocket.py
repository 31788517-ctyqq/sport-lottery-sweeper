"""
WebSocket相关功能模块
提供WebSocket连接管理和消息通知功能
"""
from typing import List
from fastapi import WebSocket
import json

from .websocket_handler import manager


async def notify_system_message(message: str):
    """
    发送系统消息到所有连接的WebSocket客户端
    
    Args:
        message: 要发送的消息内容
    """
    try:
        # 构建系统消息
        system_msg = {
            "type": "system",
            "message": message,
            "timestamp": __import__('datetime').datetime.now().isoformat()
        }
        
        # 广播消息给所有连接的客户端
        await manager.broadcast(json.dumps(system_msg))
    except Exception as e:
        print(f"发送系统消息失败: {str(e)}")


# 导出WebSocket管理器
__all__ = ["notify_system_message", "manager"]