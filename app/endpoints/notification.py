from fastapi import WebSocket, APIRouter, WebSocketDisconnect, Query
from typing import List, Optional

from app.db.get_db import SessionDep
from app.functions.notification import get_notifications
from app.models.notification import Notification

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
            message = await websocket.receive_text()
    except WebSocketDisconnect:
        alerts_manager.disconnect(websocket)


async def broadcast_alert(alert: dict, db):
    try:
        db_notification = Notification(
            type=alert.get('type'),
            message=alert.get('message'),
            month=alert.get('month'),
            year=alert.get('year'),
            difference_rate=alert.get('difference_rate'),
            threshold=alert.get('threshold'),
            meal_id=alert.get('meal_id'),
            user_id=alert.get('user_id'),
            timestamp=alert.get('timestamp')
        )

        db.add(db_notification)
        await db.commit()
        await db.refresh(db_notification)

        websocket_data = {
            "id": db_notification.id,
            "type": db_notification.type,
            "message": db_notification.message,
            "month": db_notification.month,
            "year": db_notification.year,
            "difference_rate": db_notification.difference_rate,
            "threshold": db_notification.threshold,
            "meal_id": db_notification.meal_id,
            "user_id": db_notification.user_id,
            "timestamp": db_notification.timestamp
        }

        try:
            await alerts_manager.broadcast(websocket_data)
            print(f"✅ Notification saved (ID: {db_notification.id}) and broadcasted")
        except Exception as e:
            print(f"❌ Broadcast error: {e}")

        return db_notification
    except Exception as e:
        await db.rollback()
        print("❌ Broadcast error:", e)
        return None


@router.get("/notifications")
async def get_notifications_api(
    db: SessionDep,
    limit: int = Query(50, ge=1, le=100),
    page: int = Query(1, ge=1),
    type: Optional[str] = Query(None, description="Filter by notification type"),
):
    """REST API to get existing notifications - called on page load"""
    notifications, total_count = await get_notifications(db, limit, page, type)
    return {
        "notifications": notifications,
        "total_count": total_count
    }
