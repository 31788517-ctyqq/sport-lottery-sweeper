from typing import Dict, Any, List
from enum import Enum
import json
import asyncio
import logging

logger = logging.getLogger(__name__)


class MessageType(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    TASK_ASSIGNMENT = "task_assignment"


class Message:
    def __init__(self, msg_type: MessageType, sender: str, receiver: str, content: Dict[str, Any]):
        self.type = msg_type
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.timestamp = asyncio.get_event_loop().time()
    
    def to_json(self) -> str:
        return json.dumps({
            "type": self.type.value,
            "sender": self.sender,
            "receiver": self.receiver,
            "content": self.content,
            "timestamp": self.timestamp
        })
    
    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        msg_type = MessageType(data["type"])
        return cls(msg_type, data["sender"], data["receiver"], data["content"])


class CommunicationHub:
    def __init__(self):
        self.agents = {}
        self.message_queue = asyncio.Queue()
        self.logger = logging.getLogger(__name__)
        
    def register_agent(self, agent_id: str, agent_callback):
        """注册智能体"""
        self.agents[agent_id] = agent_callback
        self.logger.info(f"Agent {agent_id} registered successfully")
        
    async def send_message(self, message: Message):
        """发送消息到指定智能体"""
        if message.receiver in self.agents:
            await self.agents[message.receiver](message)
            self.logger.debug(f"Message sent from {message.sender} to {message.receiver}")
        elif message.receiver == "broadcast":
            # 广播消息给所有智能体
            for agent_id, callback in self.agents.items():
                if agent_id != message.sender:  # 不发送给自己
                    await callback(message)
            self.logger.debug(f"Broadcast message from {message.sender}")
                    
    async def broadcast_message(self, message: Message):
        """广播消息给所有智能体"""
        message.receiver = "broadcast"
        await self.send_message(message)
    
    async def get_agent_status(self):
        """获取所有已注册智能体的状态"""
        status = {}
        for agent_id in self.agents:
            status[agent_id] = "active"
        return status