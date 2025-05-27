from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.meal_ingredient import Meal, Ingredient, MealIngredient


async def estimate_portions(db: AsyncSession) -> list[dict]:
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

    return list(meal_map.values())



