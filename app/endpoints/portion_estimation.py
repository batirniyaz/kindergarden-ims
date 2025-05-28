from fastapi import WebSocket, APIRouter, WebSocketDisconnect
from typing import List

from sqlalchemy import delete

from app.db.get_db import SessionDep
from app.functions.portion_estimation import estimate_portions, get_portion_estimation
from app.models.portion_estimation import PortionEstimation

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
    try:
        portions_data = await estimate_portions(db)

        await db.execute(delete(PortionEstimation))

        for meal_data in portions_data:
            new_record = PortionEstimation(
                meal_id=meal_data["meal_id"],
                meal_name=meal_data["meal_name"],
                portion_count=meal_data["portion_count"]
            )
            db.add(new_record)

        await db.commit()

        try:
            await manager.broadcast(portions_data)
            print(f"✅ Broadcasted {len(portions_data)} portion updates")
        except Exception as e:
            print("❌ Broadcast error:", e)

        return portions_data

    except Exception as e:
        await db.rollback()
        print(f"❌ Error in save_and_broadcast_portions: {e}")
        raise


@router.get("/portions")
async def get_portions_api(
    db: SessionDep,
    limit: int = 20,
    page: int = 1,
):
    """REST API to get existing portions - called on page load"""
    portions, total_count = await get_portion_estimation(db, limit, page)
    return {
        "portions": portions,
        "total_count": total_count,
    }
