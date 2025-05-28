from typing import Optional

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.endpoints.portion_estimation import broadcast_portion_updates
from app.ingredient.crud import get_ingredient
from app.models.delivery import IngredientDelivery
from app.schemas.delivery import IngredientDeliveryCreate
from app.celery.tasks import generate_ingredient_usage

from datetime import date


async def create_delivery(db: AsyncSession, current_user, delivery: IngredientDeliveryCreate) -> IngredientDelivery:
    try:
        db_delivery = IngredientDelivery(**delivery.model_dump(), accepted=current_user['id'])
        db.add(db_delivery)

        ingredient = await get_ingredient(db, delivery.ingredient_id)
        ingredient.weight += delivery.weight

        await db.commit()
        await db.refresh(db_delivery)

        await broadcast_portion_updates(db)

        generate_ingredient_usage.delay({
            "ingredient_id": None,
            "start_date": None,
            "end_date": None,
            "group_by": "day"
        })

        return db_delivery
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Delivery with ID {delivery.id} already exists.") from e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_deliveries(
        db: AsyncSession,
        limit: int = 10,
        page: int = 1,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        accepted: Optional[int] = None
) -> tuple[list[IngredientDelivery], int]:
    try:
        stmt = select(IngredientDelivery)
        if accepted is not None:
            stmt = stmt.filter(IngredientDelivery.accepted == accepted)
        if start_date:
            stmt = stmt.filter(IngredientDelivery.created_at >= start_date)
        if end_date:
            stmt = stmt.filter(IngredientDelivery.created_at <= end_date)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = await db.scalar(count_stmt)

        query = stmt.order_by(IngredientDelivery.created_at.desc())
        query = query.limit(limit).offset((page - 1) * limit)

        result = await db.execute(query)
        deliveries = result.scalars().all()
        return deliveries or [], total_count or 0
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_delivery(db: AsyncSession, delivery_id: int) -> IngredientDelivery:
    res = await db.execute(select(IngredientDelivery).filter_by(id=delivery_id))
    db_delivery = res.scalars().first()
    if not db_delivery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
    return db_delivery


async def delete_delivery(db: AsyncSession, delivery_id: int):
    try:
        db_delivery = await get_delivery(db, delivery_id)
        await db.delete(db_delivery)
        await db.commit()
        return {"msg": "Delivery deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))