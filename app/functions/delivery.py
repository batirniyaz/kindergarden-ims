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


async def get_deliveries(db: AsyncSession, limit: int = 10, page: int = 1) -> tuple[list[IngredientDelivery], int]:
    try:
        total_count = await db.scalar(select(func.count(IngredientDelivery.id)))
        query = select(IngredientDelivery).limit(limit).offset((page - 1) * limit)
        result = await db.execute   (query)
        deliveries = result.scalars().all()
        return deliveries or [], total_count
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