import calendar
from datetime import datetime, date
from typing import Any, Dict, List

from sqlalchemy import func, case
from sqlalchemy.future import select

from fastapi import APIRouter

from app.db.get_db import SessionDep
from app.models.delivery import IngredientDelivery
from app.models.meal_ingredient import Ingredient, MealIngredient
from app.models.serve_meal import MealServing


router = APIRouter()


@router.get('/', response_model=List[Dict[str, Any]])
async def get_ingredient_analysis_for_month(
        db: SessionDep,
        year: int = None,
        month: int = None
) -> List[Dict[str, Any]]:
    """
    Get detailed breakdown of ingredient usage, deliveries, and availability for a specific month.
    """

    if not year:
        year = datetime.now().year
    if not month:
        month = datetime.now().month

    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])

    query = (
        select(
            Ingredient.id,
            Ingredient.name,
            Ingredient.weight.label('unit_weight'),
            func.coalesce(
                func.sum(
                    case(
                        (IngredientDelivery.created_at.between(first_day, last_day), IngredientDelivery.weight),
                        else_=0
                    )
                ), 0
            ).label('delivered_this_month'),
            func.coalesce(
                func.sum(
                    case(
                        (MealServing.created_at.between(first_day, last_day), MealIngredient.weight),
                        else_=0
                    )
                ), 0
            ).label('consumed_this_month'),
            func.count(
                case(
                    (MealServing.created_at.between(first_day, last_day), MealServing.id),
                    else_=None
                )
            ).label('servings_count')
        )
        .select_from(Ingredient)
        .outerjoin(IngredientDelivery, Ingredient.id == IngredientDelivery.ingredient_id)
        .outerjoin(MealIngredient, Ingredient.id == MealIngredient.ingredient_id)
        .outerjoin(MealServing, MealIngredient.meal_id == MealServing.meal_id)
        .group_by(Ingredient.id, Ingredient.name, Ingredient.weight)
        .order_by(Ingredient.name)
    )

    result = await db.execute(query)
    return [dict(row._mapping) for row in result.fetchall()]
