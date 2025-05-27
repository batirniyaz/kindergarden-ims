from datetime import datetime

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.endpoints.notification import alerts_manager
from app.endpoints.portion_estimation import broadcast_portion_updates
from app.models.meal_ingredient import MealIngredient, Ingredient
from app.models.serve_meal import MealServing
from app.schemas.serve_meal import ServeMealCreate, ServeMealRead, ServeMealListResponse


async def create_serve_meal(db: AsyncSession, current_user, serve_meal: ServeMealCreate) -> MealServing:
    stmt = (select(MealIngredient, Ingredient)
            .join(Ingredient, MealIngredient.ingredient_id == Ingredient.id)
            .where(MealIngredient.meal_id == serve_meal.meal_id))

    res = await db.execute(stmt)
    rows = res.all()
    insufficient = [ing.name for mi, ing in rows if ing.weight < mi.weight]
    if insufficient:

        await alerts_manager.broadcast({
            "type": "insufficient_stock",
            "meal_id": serve_meal.meal_id,
            "user_id": current_user["id"],
            "message": f"Cannot serve meal {serve_meal.meal_id}: insufficient inventory for {', '.join(insufficient)}",
            "timestamp": datetime.now().isoformat()
        })

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Not enough inventory for: {', '.join(insufficient)}"
        )

    try:
        for mi, ing in rows:
            ing.weight -= mi.weight
            db.add(ing)

        serving = MealServing(
            meal_id=serve_meal.meal_id,
            served_by=current_user['id']
        )

        db.add(serving)
        await db.commit()
        await db.refresh(serving)

        await broadcast_portion_updates(db)

        return serving
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def get_serve_meals(db: AsyncSession, limit: int = 10, page: int = 1) -> tuple[list[MealServing], int]:
    try:
        total_count = await db.scalar(select(func.count()).select_from(MealServing))
        query = (
            select(MealServing).limit(limit).offset((page - 1) * limit))
        result = await db.execute(query)
        serve_meals = result.scalars().all()
        return serve_meals or [], total_count
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
