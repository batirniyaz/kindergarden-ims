from typing import Optional, List, Dict

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


async def get_notifications(
        db: AsyncSession,
        limit: int = 50,
        page: int = 1,
        notification_type: Optional[str] = None
) -> tuple[List[Dict], int]:
    """Get notifications from database - for page load"""

    # Build query with optional filters
    query = select(Notification)
    if notification_type:
        query = query.where(Notification.type == notification_type)

    # Get total count
    count_query = select(func.count(Notification.id))
    if notification_type:
        count_query = count_query.where(Notification.type == notification_type)

    total_count = await db.scalar(count_query)

    # Get paginated results
    query = (query.order_by(Notification.timestamp.desc())
             .limit(limit)
             .offset((page - 1) * limit))

    result = await db.execute(query)
    notifications = result.scalars().all()

    # Convert to dict format
    notifications_data = [
        {
            "id": n.id,
            "type": n.type,
            "message": n.message,
            "month": n.month,
            "year": n.year,
            "difference_rate": n.difference_rate,
            "threshold": n.threshold,
            "meal_id": n.meal_id,
            "user_id": n.user_id,
            "timestamp": n.timestamp
        }
        for n in notifications
    ]

    return notifications_data, total_count
