from datetime import date
from typing import Optional, List, Dict, Any

from fastapi import HTTPException
from sqlalchemy import func, literal_column, union_all
from sqlalchemy.future import select

from fastapi import APIRouter

from app.db.get_db import SessionDep
from app.models.delivery import IngredientDelivery
from app.models.meal_ingredient import Ingredient, MealIngredient, Meal
from app.models.serve_meal import MealServing

router = APIRouter()


@router.get("/", response_model=list[dict])
async def get_ingredient_usage_over_time(
        db: SessionDep,
        ingredient_id: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        group_by: str = 'day'  # 'day', 'week', 'month'
) -> List[Dict[str, Any]]:
    """
    Get ingredient usage over time including both consumption (from meal servings)
    and delivery data.

    Args:
        ingredient_id: Filter by specific ingredient (optional)
        start_date: Start date for filtering (optional)
        end_date: End date for filtering (optional)
        group_by: Grouping period - 'day', 'week', or 'month'
        :param group_by:
        :param end_date:
        :param start_date:
        :param ingredient_id:
        :param db:
    """

    # Define date truncation based on group_by parameter
    if group_by == 'day':
        date_trunc = func.date(func.timezone('UTC', MealServing.created_at))
        delivery_date_trunc = func.date(func.timezone('UTC', IngredientDelivery.created_at))
    elif group_by == 'week':
        date_trunc = func.date_trunc('week', func.timezone('UTC', MealServing.created_at))
        delivery_date_trunc = func.date_trunc('week', func.timezone('UTC', IngredientDelivery.created_at))
    else:  # month
        date_trunc = func.date_trunc('month', func.timezone('UTC', MealServing.created_at))
        delivery_date_trunc = func.date_trunc('month', func.timezone('UTC', IngredientDelivery.created_at))

    # Consumption subquery - calculate ingredient usage from meal servings
    consumption_query = (
        select(
            Ingredient.id.label('ingredient_id'),
            Ingredient.name.label('ingredient_name'),
            date_trunc.label('period'),
            func.sum(MealIngredient.weight).label('consumed_weight'),
            func.count(MealServing.id).label('servings_count')
        )
        .select_from(MealServing)
        .join(Meal, MealServing.meal_id == Meal.id)
        .join(MealIngredient, Meal.id == MealIngredient.meal_id)
        .join(Ingredient, MealIngredient.ingredient_id == Ingredient.id)
    )

    # Delivery subquery - calculate ingredient deliveries
    delivery_query = (
        select(
            Ingredient.id.label('ingredient_id'),
            Ingredient.name.label('ingredient_name'),
            delivery_date_trunc.label('period'),
            func.sum(IngredientDelivery.weight).label('delivered_weight'),
            func.count(IngredientDelivery.id).label('delivery_count')
        )
        .select_from(IngredientDelivery)
        .join(Ingredient, IngredientDelivery.ingredient_id == Ingredient.id)
    )

    # Apply filters
    if ingredient_id:
        consumption_query = consumption_query.where(Ingredient.id == ingredient_id)
        delivery_query = delivery_query.where(Ingredient.id == ingredient_id)

    if start_date:
        consumption_query = consumption_query.where(func.date(MealServing.created_at) >= start_date)
        delivery_query = delivery_query.where(func.date(IngredientDelivery.created_at) >= start_date)

    if end_date:
        consumption_query = consumption_query.where(func.date(MealServing.created_at) <= end_date)
        delivery_query = delivery_query.where(func.date(IngredientDelivery.created_at) <= end_date)

    # Group by period and ingredient
    consumption_query = consumption_query.group_by(
        Ingredient.id, Ingredient.name, date_trunc
    ).subquery()

    delivery_query = delivery_query.group_by(
        Ingredient.id, Ingredient.name, delivery_date_trunc
    ).subquery()

    # Combine consumption and delivery data with FULL OUTER JOIN
    final_query = (
        select(
            func.coalesce(consumption_query.c.ingredient_id, delivery_query.c.ingredient_id).label('ingredient_id'),
            func.coalesce(consumption_query.c.ingredient_name, delivery_query.c.ingredient_name).label(
                'ingredient_name'),
            func.coalesce(consumption_query.c.period, delivery_query.c.period).label('period'),
            func.coalesce(consumption_query.c.consumed_weight, 0).label('consumed_weight'),
            func.coalesce(consumption_query.c.servings_count, 0).label('servings_count'),
            func.coalesce(delivery_query.c.delivered_weight, 0).label('delivered_weight'),
            func.coalesce(delivery_query.c.delivery_count, 0).label('delivery_count')
        )
        .select_from(
            consumption_query.outerjoin(
                delivery_query,
                (consumption_query.c.ingredient_id == delivery_query.c.ingredient_id) &
                (consumption_query.c.period == delivery_query.c.period)
            )
        )
        .order_by('period', 'ingredient_name')
    )

    result = await db.execute(final_query)
    return [dict(row._mapping) for row in result.fetchall()]
