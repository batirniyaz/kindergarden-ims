import calendar
from datetime import datetime, date
from typing import Any, Dict

from sqlalchemy import func, case
from sqlalchemy.future import select

from fastapi import APIRouter

from app.db.get_db import SessionDep
from app.endpoints.notification import alerts_manager
from app.models.delivery import IngredientDelivery
from app.models.meal_ingredient import MealIngredient, Meal
from app.models.serve_meal import MealServing

router = APIRouter()


@router.get("/", response_model=Dict[str, Any])
async def get_monthly_summary_report(
        db: SessionDep,
        year: int = None,
        month: int = None,
        threshold_percentage: float = 15.0
) -> Dict[str, Any]:
    """
    Generate monthly summary showing per-meal analysis:
    - Portions served per meal in the month
    - Total portions that could be served based on total delivered ingredients (not remaining)
    - Difference rate and misuse flag per meal

    Args:
        year: Specific year (default: current year)
        month: Specific month (default: current month)
        threshold_percentage: Threshold for flagging potential misuse
    """

    if not year:
        year = datetime.now().year
    if not month:
        month = datetime.now().month

    # Get first and last day of the month
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])

    # Query 1: Get total ingredient deliveries (cumulative - all time up to month end)
    total_ingredient_deliveries_query = (
        select(
            IngredientDelivery.ingredient_id,
            func.sum(IngredientDelivery.weight).label('total_delivered')
        )
        .select_from(IngredientDelivery)
        .where(func.date(IngredientDelivery.created_at) <= last_day)
        .group_by(IngredientDelivery.ingredient_id)
        .subquery()
    )

    # Query 2: Get actual servings count per meal (separate from ingredients calculation)
    actual_servings_per_meal_query = (
        select(
            Meal.id.label('meal_id'),
            Meal.name.label('meal_name'),
            func.count(
                case(
                    (func.date(MealServing.created_at).between(first_day, last_day), MealServing.id),
                    else_=None
                )
            ).label('portions_served_this_month')
        )
        .select_from(Meal)
        .outerjoin(MealServing, Meal.id == MealServing.meal_id)
        .group_by(Meal.id, Meal.name)
        .subquery()
    )

    # Query 3: Calculate maximum possible servings based on ingredients (separate query)
    max_possible_servings_query = (
        select(
            Meal.id.label('meal_id'),
            func.min(
                func.floor(
                    total_ingredient_deliveries_query.c.total_delivered / MealIngredient.weight
                )
            ).label('max_possible_servings_from_deliveries')
        )
        .select_from(Meal)
        .join(MealIngredient, Meal.id == MealIngredient.meal_id)
        .join(total_ingredient_deliveries_query,
              MealIngredient.ingredient_id == total_ingredient_deliveries_query.c.ingredient_id)
        .group_by(Meal.id)
        .subquery()
    )

    # Query 4: Combine the results
    meal_analysis_query = (
        select(
            actual_servings_per_meal_query.c.meal_id,
            actual_servings_per_meal_query.c.meal_name,
            actual_servings_per_meal_query.c.portions_served_this_month,
            func.coalesce(max_possible_servings_query.c.max_possible_servings_from_deliveries, 0).label(
                'max_possible_servings_from_deliveries')
        )
        .select_from(actual_servings_per_meal_query)
        .outerjoin(max_possible_servings_query,
                   actual_servings_per_meal_query.c.meal_id == max_possible_servings_query.c.meal_id)
        .subquery()
    )

    # Execute the query to get per-meal data
    res = await db.execute(select(meal_analysis_query))
    meal_analysis = res.fetchall()

    meal_summaries = []
    total_served_all_meals = 0
    total_could_serve_all_meals = 0

    for row in meal_analysis:
        portions_served = row.portions_served_this_month
        max_possible = row.max_possible_servings_from_deliveries or 0

        # Calculate difference rate for this meal
        if max_possible > 0:
            difference_rate = ((max_possible - portions_served) / max_possible) * 100
        else:
            difference_rate = 0

        # Flag potential misuse for this meal
        potential_misuse = difference_rate < threshold_percentage  # Negative because over-serving is the issue

        meal_summary = {
            'meal_id': row.meal_id,
            'meal_name': row.meal_name,
            'portions_served_this_month': portions_served,
            'max_possible_servings_from_total_deliveries': max_possible,
            'difference_rate_percentage': round(difference_rate, 2),
            'potential_misuse_flag': potential_misuse,
            'summary': f"Meal '{row.meal_name}': Served {portions_served} out of {max_possible} possible ({difference_rate:.1f}% difference)"
        }

        meal_summaries.append(meal_summary)
        total_served_all_meals += portions_served
        total_could_serve_all_meals += max_possible

    # Calculate overall difference rate
    if total_could_serve_all_meals > 0:
        overall_difference_rate = ((total_could_serve_all_meals - total_served_all_meals) / total_could_serve_all_meals) * 100
    else:
        overall_difference_rate = 0

    # Overall misuse flag (if any meal has misuse or overall over-serving)
    overall_misuse = (overall_difference_rate < -threshold_percentage or
                      any(meal['potential_misuse_flag'] for meal in meal_summaries))

    report = {
        'month': month,
        'year': year,
        'meal_summaries': meal_summaries,
        'overall_summary': {
            'total_portions_served_all_meals': total_served_all_meals,
            'total_portions_could_serve_all_meals': total_could_serve_all_meals,
            'overall_difference_rate_percentage': round(overall_difference_rate, 2),
            'overall_potential_misuse_flag': overall_misuse,
            'threshold_percentage': threshold_percentage,
            'summary': f"Overall: Served {total_served_all_meals} out of {total_could_serve_all_meals} possible portions ({overall_difference_rate:.1f}% difference)"
        }
    }

    if overall_misuse:
        await alerts_manager.broadcast({
            'type': 'monthly_discrepancy',
            'month': month,
            'year': year,
            'difference_rate': round(overall_difference_rate, 2),
            'threshold': threshold_percentage,
            'message': report['overall_summary']['summary'],
            'timestamp': datetime.now().isoformat()
        })

    return report

