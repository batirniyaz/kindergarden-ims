from sqlalchemy import func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.meal_ingredient import Meal, Ingredient, MealIngredient
from app.models.portion_estimation import PortionEstimation


async def estimate_portions(db: AsyncSession) -> list[dict]:
    await db.execute(delete(PortionEstimation))

    stmt = (select(Meal.id, Meal.name, MealIngredient, Ingredient)
            .join(MealIngredient, Meal.id == MealIngredient.meal_id)
            .join(Ingredient, MealIngredient.ingredient_id == Ingredient.id))
    result = await db.execute(stmt)
    rows = result.all()

    meal_map = {}
    for meal_id, meal_name, mi, ing in rows:
        meal_map.setdefault(meal_id, {
            "meal_id": meal_id,
            "meal_name": meal_name,
            "portion_count": float('inf')
        })

        if mi.weight == 0:
            continue
        possible = ing.weight // mi.weight
        meal_map[meal_id]["portion_count"] = min(meal_map[meal_id]["portion_count"], possible)

    for meal in meal_map.values():
        if meal["portion_count"] == float('inf'):
            meal["portion_count"] = 0
        # Ensure portion_count is an integer
        meal["portion_count"] = int(meal["portion_count"])

    for meal_data in meal_map.values():
        new_record = PortionEstimation(
            meal_id=meal_data["meal_id"],
            meal_name=meal_data["meal_name"],
            portion_count=meal_data["portion_count"]
        )
        db.add(new_record)

    await db.commit()


    return list(meal_map.values())


async def get_portion_estimation(db: AsyncSession, limit: int = 20, page: int = 1):
    total_count = await db.scalar(select(func.count(PortionEstimation.id)))
    stmt = select(PortionEstimation).order_by(PortionEstimation.id.desc()).limit(limit).offset((page - 1) * limit)
    result = await db.execute(stmt)
    portions = result.scalars().all()

    portions_data = [
        {
            "meal_id": p.meal_id,
            "meal_name": p.meal_name,
            "portion_count": p.portion_count,
            "id": p.id
        }
        for p in portions
    ]

    return portions_data, total_count



