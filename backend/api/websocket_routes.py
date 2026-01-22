from fastapi import APIRouter, WebSocket
from ..services.match_service import match_service
import asyncio
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.websocket("/ws/matches")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            matches = await match_service.get_all_matches()

            # 仅推送增量更新的数据
            updated_matches = [m for m in matches if m.get("is_new", False)]
            if updated_matches:
                await websocket.send_json({"updated_matches": updated_matches})

            await asyncio.sleep(10)  # 每 10 秒推送一次数据
    except Exception as e:
        logger.error(f"WebSocket 连接关闭: {e}")
    finally:
        await websocket.close()