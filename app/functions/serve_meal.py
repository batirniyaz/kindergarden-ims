from datetime import datetime, date
from typing import Optional

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.endpoints.notification import broadcast_alert
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

        await broadcast_alert({
            "type": "insufficient_stock",
            "meal_id": serve_meal.meal_id,
            "user_id": current_user["id"],
            "message": f"Cannot serve meal {serve_meal.meal_id}: insufficient inventory for {', '.join(insufficient)}",
            "timestamp": datetime.now().isoformat()
        }, db)

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


async def get_serve_meals(
    db: AsyncSession,
    limit: int = 10,
    page: int = 1,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    served_by: Optional[int] = None,
) -> tuple[list[MealServing], int]:
    try:
        stmt = select(MealServing)
        if served_by is not None:
            stmt = stmt.filter(MealServing.served_by == served_by)
        if start_date:
            stmt = stmt.filter(MealServing.created_at >= start_date)
        if end_date:
            stmt = stmt.filter(MealServing.created_at <= end_date)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total_count = await db.scalar(count_stmt)

        query = stmt.order_by(MealServing.created_at.desc())
        query = query.limit(limit).offset((page - 1) * limit)

        result = await db.execute(query)
        serve_meals = result.scalars().all()
        return serve_meals or [], total_count or 0
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
