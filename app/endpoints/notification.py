from fastapi import WebSocket, APIRouter, WebSocketDisconnect
from typing import List

router = APIRouter()


class AlertsManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        self.active.remove(ws)

    async def broadcast(self, alert: dict):
        for connection in self.active:
            await connection.send_json(alert)

alerts_manager = AlertsManager()


@router.websocket("/alerts")
async def alerts_ws(websocket: WebSocket):
    await alerts_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        alerts_manager.disconnect(websocket)
