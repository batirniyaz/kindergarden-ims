from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.meal_ingredient import Ingredient
from app.ingredient.schema import IngredientCreate


async def create_ingredient(db: AsyncSession, ingredient: IngredientCreate) -> Ingredient:
    try:
        db_ingredient = Ingredient(**ingredient.model_dump(), weight=0)
        db.add(db_ingredient)
        await db.commit()
        await db.refresh(db_ingredient)
        return db_ingredient
    except IntegrityError as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Ingredient with name {ingredient.name} already exists.") from e
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_ingredients(db: AsyncSession, limit: int = 10, page: int = 1) -> tuple[list[Ingredient], int]:
    try:
        total_count = await db.scalar(select(func.count(Ingredient.id)))
        query = select(Ingredient).limit(limit).offset((page - 1) * limit)
        result = await db.execute(query)
        ingredients = result.scalars().all()
        return ingredients or [], total_count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_ingredient(db: AsyncSession, ingredient_id: int) -> Ingredient:
    res = await db.execute(select(Ingredient).filter_by(id=ingredient_id))
    db_ingredient = res.scalars().first()
    if not db_ingredient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")
    return db_ingredient


async def delete_ingredient(db: AsyncSession, ingredient_id: int):
    try:
        db_ingredient = await get_ingredient(db, ingredient_id)

        await db.delete(db_ingredient)
        await db.commit()
        return {"msg": "Ingredient deleted successfully"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

