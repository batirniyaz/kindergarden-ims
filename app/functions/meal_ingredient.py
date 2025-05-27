from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.endpoints.portion_estimation import broadcast_portion_updates
from app.models.meal_ingredient import MealIngredient
from app.schemas.meal_ingredient import MealIngredientCreate, MealIngredientUpdate


async def create_meal_ingredient(db: AsyncSession, meal_ingredient: MealIngredientCreate) -> MealIngredient:
    try:
        db_meal_ingredient = MealIngredient(**meal_ingredient.model_dump())
        db.add(db_meal_ingredient)
        await db.commit()
        await db.refresh(db_meal_ingredient)

        await broadcast_portion_updates(db)

        return db_meal_ingredient
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=str(e))
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_meal_ingredients(db: AsyncSession, limit: int = 10, page: int = 1) -> tuple[list[MealIngredient], int]:
    try:
        total_count = await db.scalar(select(func.count()).select_from(MealIngredient))
        query = (
            select(MealIngredient).limit(limit).offset((page - 1) * limit))
        result = await db.execute(query)
        meal_ingredients = result.scalars().all()
        return meal_ingredients or [], total_count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_meal_ingredient(db: AsyncSession, meal_id: int, ingredient_id: int) -> MealIngredient:
    res = await db.execute(select(MealIngredient).filter_by(meal_id=meal_id).filter_by(ingredient_id=ingredient_id))
    db_meal_ingredient = res.scalars().first()
    if not db_meal_ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meal ingredient pair not found")
    return db_meal_ingredient


async def update_meal_ingredient(db: AsyncSession, meal_id: int, ingredient_id: int, meal_ingredient: MealIngredientUpdate) -> MealIngredient:
    try:
        db_meal_ingredient = await get_meal_ingredient(db, meal_id, ingredient_id)

        for key, value in meal_ingredient.model_dump(exclude_unset=True).items():
            setattr(db_meal_ingredient, key, value)

        await db.commit()
        await db.refresh(db_meal_ingredient)

        await broadcast_portion_updates(db)

        return db_meal_ingredient
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def delete_meal_ingredient(db: AsyncSession, meal_id: int, ingredient_id: int):
    try:
        db_meal_ingredient = await get_meal_ingredient(db, meal_id, ingredient_id)
        await db.delete(db_meal_ingredient)
        await db.commit()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
