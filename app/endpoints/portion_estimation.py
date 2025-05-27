from fastapi import WebSocket, APIRouter, WebSocketDisconnect
from typing import List

from app.functions.portion_estimation import estimate_portions

router = APIRouter()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, data):
        for connection in self.active_connections:
            await connection.send_json(data)


manager = ConnectionManager()


@router.websocket("/stream")
async def portions_ws(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            message = await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


async def broadcast_portion_updates(db):
    data = await estimate_portions(db)
    try:
        await manager.broadcast(data)
    except Exception as e:
        print("❌ Broadcast error:", e)
