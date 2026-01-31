from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
import json

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()


@router.websocket("/ws/matches")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 解析接收到的数据
            try:
                parsed_data = json.loads(data)
                message_type = parsed_data.get("type")
                
                if message_type == "subscribe":
                    # 处理订阅请求
                    subscription_data = {
                        "type": "subscription_success",
                        "message": "Successfully subscribed to match updates"
                    }
                    await manager.send_personal_message(json.dumps(subscription_data), websocket)
                elif message_type == "unsubscribe":
                    # 处理取消订阅请求
                    break
                else:
                    # 广播普通消息
                    await manager.broadcast(f"Client says: {data}")
            except json.JSONDecodeError:
                await manager.send_personal_message("Invalid JSON format", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast("A client disconnected")