from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func

from fastapi import HTTPException, status

from app.meal.schema import MealCreate
from app.models.meal_ingredient import Meal


async def create_meal(db: AsyncSession, meal: MealCreate, user_id: int) -> Meal:
    try:
        db_meal = Meal(**meal.model_dump(), added_by=user_id)
        db.add(db_meal)
        await db.commit()
        await db.refresh(db_meal)
        return db_meal
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Meal with name {meal.name} already exists.") from e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_meals(db: AsyncSession, limit: int = 10, page: int = 1) -> tuple[list[Meal], int]:
    try:
        total_count = await db.scalar(select(func.count(Meal.id)))
        query = select(Meal).limit(limit).offset((page - 1) * limit)
        result = await db.execute(query)
        meals = result.scalars().all()
        return meals or [], total_count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_meal(db: AsyncSession, meal_id: int) -> Meal:
    res = await db.execute(select(Meal).filter_by(id=meal_id))
    db_meal = res.scalars().first()
    if not db_meal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal not found")
    return db_meal


async def delete_meal(db: AsyncSession, meal_id: int):
    try:
        db_meal = await get_meal(db, meal_id)
        await db.delete(db_meal)
        await db.commit()
        return {"detail": "Meal deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
