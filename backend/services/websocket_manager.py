"""
智能体WebSocket通信管理器
提供实时状态更新、控制指令、告警推送等功能
"""

import asyncio
import json
import logging
from typing import Dict, Set, Any, List, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class WebSocketMessageType(Enum):
    """WebSocket消息类型"""
    AGENT_STATUS = "agent_status"
    AGENT_METRICS = "agent_metrics"
    AGENT_ALERT = "agent_alert"
    AGENT_CONTROL = "agent_control"
    AGENT_EXECUTION = "agent_execution"
    SYSTEM_HEALTH = "system_health"
    ERROR = "error"
    ACK = "ack"


class WebSocketConnection:
    """WebSocket连接管理"""
    
    def __init__(self, websocket: WebSocket, connection_id: str):
        self.websocket = websocket
        self.connection_id = connection_id
        self.subscriptions: Set[str] = set()
        self.authenticated: bool = False
        self.user_info: Optional[Dict[str, Any]] = None
        self.connected_at = datetime.now()
        self.last_activity = datetime.now()
    
    def subscribe(self, topic: str):
        """订阅主题"""
        self.subscriptions.add(topic)
        logger.info(f"连接 {self.connection_id} 订阅主题: {topic}")
    
    def unsubscribe(self, topic: str):
        """取消订阅主题"""
        if topic in self.subscriptions:
            self.subscriptions.remove(topic)
            logger.info(f"连接 {self.connection_id} 取消订阅主题: {topic}")
    
    def has_subscription(self, topic: str) -> bool:
        """检查是否订阅了指定主题"""
        return topic in self.subscriptions
    
    def update_activity(self):
        """更新活动时间"""
        self.last_activity = datetime.now()


class AgentWebSocketManager:
    """智能体WebSocket管理器"""
    
    def __init__(self):
        self.connections: Dict[str, WebSocketConnection] = {}
        self.agent_connections: Dict[str, Set[str]] = {}  # 智能体ID -> 连接ID集合
        self.topic_connections: Dict[str, Set[str]] = {}  # 主题 -> 连接ID集合
        
        # 消息队列
        self.message_queue = asyncio.Queue()
        
        # 启动消息分发任务
        self._dispatcher_task = asyncio.create_task(self._message_dispatcher())
        
        logger.info("智能体WebSocket管理器初始化完成")
    
    async def connect(self, websocket: WebSocket) -> str:
        """接受WebSocket连接"""
        await websocket.accept()
        
        connection_id = str(uuid.uuid4())
        connection = WebSocketConnection(websocket, connection_id)
        self.connections[connection_id] = connection
        
        logger.info(f"WebSocket连接已建立: {connection_id}")
        
        # 发送连接确认消息
        await self._send_to_connection(connection_id, {
            "type": WebSocketMessageType.ACK.value,
            "connection_id": connection_id,
            "message": "连接已建立",
            "timestamp": datetime.now().isoformat()
        })
        
        return connection_id
    
    async def disconnect(self, connection_id: str):
        """断开WebSocket连接"""
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            
            # 清理订阅关系
            for topic in list(connection.subscriptions):
                self.unsubscribe(connection_id, topic)
            
            # 清理智能体关联
            for agent_id, connections_set in list(self.agent_connections.items()):
                if connection_id in connections_set:
                    connections_set.remove(connection_id)
                    if not connections_set:
                        del self.agent_connections[agent_id]
            
            del self.connections[connection_id]
            logger.info(f"WebSocket连接已断开: {connection_id}")
    
    async def handle_message(self, connection_id: str, message: Dict[str, Any]):
        """处理WebSocket消息"""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        connection.update_activity()
        
        message_type = message.get("type")
        
        try:
            if message_type == "subscribe":
                await self._handle_subscribe(connection_id, message)
            elif message_type == "unsubscribe":
                await self._handle_unsubscribe(connection_id, message)
            elif message_type == "control":
                await self._handle_control(connection_id, message)
            elif message_type == "ping":
                await self._handle_ping(connection_id, message)
            else:
                await self._send_to_connection(connection_id, {
                    "type": WebSocketMessageType.ERROR.value,
                    "error": f"未知的消息类型: {message_type}",
                    "timestamp": datetime.now().isoformat()
                })
                
        except Exception as e:
            logger.error(f"处理WebSocket消息失败: {e}")
            await self._send_to_connection(connection_id, {
                "type": WebSocketMessageType.ERROR.value,
                "error": f"消息处理失败: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
    
    async def subscribe(self, connection_id: str, topic: str):
        """订阅主题"""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        connection.subscribe(topic)
        
        # 更新主题订阅关系
        if topic not in self.topic_connections:
            self.topic_connections[topic] = set()
        self.topic_connections[topic].add(connection_id)
        
        # 如果是智能体主题，更新智能体关联
        if topic.startswith("agent_"):
            agent_id = topic.replace("agent_", "")
            if agent_id not in self.agent_connections:
                self.agent_connections[agent_id] = set()
            self.agent_connections[agent_id].add(connection_id)
    
    def unsubscribe(self, connection_id: str, topic: str):
        """取消订阅主题"""
        if connection_id in self.connections:
            connection = self.connections[connection_id]
            connection.unsubscribe(topic)
        
        # 清理主题订阅关系
        if topic in self.topic_connections:
            if connection_id in self.topic_connections[topic]:
                self.topic_connections[topic].remove(connection_id)
                if not self.topic_connections[topic]:
                    del self.topic_connections[topic]
        
        # 清理智能体关联
        if topic.startswith("agent_"):
            agent_id = topic.replace("agent_", "")
            if agent_id in self.agent_connections:
                if connection_id in self.agent_connections[agent_id]:
                    self.agent_connections[agent_id].remove(connection_id)
                    if not self.agent_connections[agent_id]:
                        del self.agent_connections[agent_id]
    
    async def broadcast_agent_status(self, agent_id: str, status_data: Dict[str, Any]):
        """广播智能体状态更新"""
        message = {
            "type": WebSocketMessageType.AGENT_STATUS.value,
            "agent_id": agent_id,
            "data": status_data,
            "timestamp": datetime.now().isoformat()
        }
        
        await self._broadcast_to_topic(f"agent_{agent_id}", message)
        await self._broadcast_to_topic("agent_status", message)
    
    async def broadcast_agent_metrics(self, agent_id: str, metrics_data: Dict[str, Any]):
        """广播智能体指标更新"""
        message = {
            "type": WebSocketMessageType.AGENT_METRICS.value,
            "agent_id": agent_id,
            "data": metrics_data,
            "timestamp": datetime.now().isoformat()
        }
        
        await self._broadcast_to_topic(f"agent_{agent_id}", message)
        await self._broadcast_to_topic("agent_metrics", message)
    
    async def broadcast_agent_alert(self, agent_id: str, alert_data: Dict[str, Any]):
        """广播智能体告警"""
        message = {
            "type": WebSocketMessageType.AGENT_ALERT.value,
            "agent_id": agent_id,
            "data": alert_data,
            "timestamp": datetime.now().isoformat()
        }
        
        await self._broadcast_to_topic(f"agent_{agent_id}", message)
        await self._broadcast_to_topic("agent_alerts", message)
        await self._broadcast_to_topic("system_alerts", message)
    
    async def broadcast_system_health(self, health_data: Dict[str, Any]):
        """广播系统健康状态"""
        message = {
            "type": WebSocketMessageType.SYSTEM_HEALTH.value,
            "data": health_data,
            "timestamp": datetime.now().isoformat()
        }
        
        await self._broadcast_to_topic("system_health", message)
    
    async def get_connection_stats(self) -> Dict[str, Any]:
        """获取连接统计信息"""
        now = datetime.now()
        active_connections = 0
        inactive_connections = 0
        
        for connection in self.connections.values():
            time_since_activity = (now - connection.last_activity).total_seconds()
            if time_since_activity < 300:  # 5分钟内活跃
                active_connections += 1
            else:
                inactive_connections += 1
        
        return {
            "total_connections": len(self.connections),
            "active_connections": active_connections,
            "inactive_connections": inactive_connections,
            "agent_connections": len(self.agent_connections),
            "topic_connections": len(self.topic_connections),
            "timestamp": now.isoformat()
        }
    
    async def cleanup_inactive_connections(self, max_inactive_time: int = 3600):
        """清理不活跃的连接"""
        now = datetime.now()
        inactive_connections = []
        
        for connection_id, connection in self.connections.items():
            time_since_activity = (now - connection.last_activity).total_seconds()
            if time_since_activity > max_inactive_time:
                inactive_connections.append(connection_id)
        
        for connection_id in inactive_connections:
            logger.info(f"清理不活跃连接: {connection_id}")
            await self.disconnect(connection_id)
    
    async def _message_dispatcher(self):
        """消息分发器"""
        while True:
            try:
                # 从队列获取消息
                message_data = await self.message_queue.get()
                
                topic = message_data.get("topic")
                message = message_data.get("message")
                
                if topic and message:
                    await self._broadcast_to_topic(topic, message)
                
                self.message_queue.task_done()
                
            except Exception as e:
                logger.error(f"消息分发器错误: {e}")
                await asyncio.sleep(1)  # 错误后短暂延迟
    
    async def _broadcast_to_topic(self, topic: str, message: Dict[str, Any]):
        """向指定主题的所有连接广播消息"""
        if topic not in self.topic_connections:
            return
        
        connections_to_remove = []
        
        for connection_id in list(self.topic_connections[topic]):
            if connection_id not in self.connections:
                connections_to_remove.append(connection_id)
                continue
            
            try:
                await self._send_to_connection(connection_id, message)
            except Exception as e:
                logger.error(f"向连接 {connection_id} 发送消息失败: {e}")
                connections_to_remove.append(connection_id)
        
        # 清理失效的连接
        for connection_id in connections_to_remove:
            if topic in self.topic_connections:
                if connection_id in self.topic_connections[topic]:
                    self.topic_connections[topic].remove(connection_id)
    
    async def _send_to_connection(self, connection_id: str, message: Dict[str, Any]):
        """向指定连接发送消息"""
        if connection_id not in self.connections:
            return
        
        connection = self.connections[connection_id]
        
        try:
            await connection.websocket.send_json(message)
        except Exception as e:
            logger.error(f"发送消息到连接 {connection_id} 失败: {e}")
            await self.disconnect(connection_id)
    
    async def _handle_subscribe(self, connection_id: str, message: Dict[str, Any]):
        """处理订阅消息"""
        topic = message.get("topic")
        if not topic:
            await self._send_to_connection(connection_id, {
                "type": WebSocketMessageType.ERROR.value,
                "error": "订阅消息缺少topic字段",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        await self.subscribe(connection_id, topic)
        
        await self._send_to_connection(connection_id, {
            "type": WebSocketMessageType.ACK.value,
            "message": f"已成功订阅主题: {topic}",
            "topic": topic,
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_unsubscribe(self, connection_id: str, message: Dict[str, Any]):
        """处理取消订阅消息"""
        topic = message.get("topic")
        if not topic:
            await self._send_to_connection(connection_id, {
                "type": WebSocketMessageType.ERROR.value,
                "error": "取消订阅消息缺少topic字段",
                "timestamp": datetime.now().isoformat()
            })
            return
        
        self.unsubscribe(connection_id, topic)
        
        await self._send_to_connection(connection_id, {
            "type": WebSocketMessageType.ACK.value,
            "message": f"已取消订阅主题: {topic}",
            "topic": topic,
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_control(self, connection_id: str, message: Dict[str, Any]):
        """处理控制消息"""
        # 这里可以添加智能体控制逻辑
        # 暂时只返回确认消息
        
        await self._send_to_connection(connection_id, {
            "type": WebSocketMessageType.ACK.value,
            "message": "控制指令已接收",
            "control_id": message.get("control_id", "unknown"),
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_ping(self, connection_id: str, message: Dict[str, Any]):
        """处理ping消息"""
        await self._send_to_connection(connection_id, {
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        })


# 全局WebSocket管理器实例
_global_websocket_manager: Optional[AgentWebSocketManager] = None


def get_websocket_manager() -> AgentWebSocketManager:
    """获取全局WebSocket管理器"""
    global _global_websocket_manager
    
    if _global_websocket_manager is None:
        _global_websocket_manager = AgentWebSocketManager()
    
    return _global_websocket_manager


def reset_websocket_manager():
    """重置全局WebSocket管理器"""
    global _global_websocket_manager
    
    if _global_websocket_manager:
        # 清理所有连接
        for connection_id in list(_global_websocket_manager.connections.keys()):
            asyncio.create_task(_global_websocket_manager.disconnect(connection_id))
        
        _global_websocket_manager = None