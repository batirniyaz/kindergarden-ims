from fastapi import APIRouter

from app.db.get_db import SessionDep
from app.auth.util import UserDep, ManagerDep

from app.meal.schema import MealCreate, MealRead, MealListResponse
from app.meal.crud import create_meal, get_meal, delete_meal, get_meals

router = APIRouter()


@router.post("/", response_model=MealRead)
async def create_meal_endpoint(
        meal: MealCreate,
        current_user: ManagerDep,
        db: SessionDep
):
    db_meal = await create_meal(db, meal, current_user['id'])
    return MealRead.model_validate(db_meal)


@router.get("/", response_model=MealListResponse)
async def get_meals_endpoint(
        current_user: UserDep,
        db: SessionDep,
        limit: int = 10,
        page: int = 1
):
    db_meals, total_count = await get_meals(db, limit, page)
    items = [MealRead.model_validate(meal) for meal in db_meals]
    return MealListResponse(total_count=total_count, items=items)


@router.get("/{meal_id}", response_model=MealRead)
async def get_meal_endpoint(
        meal_id: int,
        current_user: UserDep,
        db: SessionDep
):
    db_meal = await get_meal(db, meal_id)
    return MealRead.model_validate(db_meal)


@router.delete("/{meal_id}")
async def delete_meal_endpoint(
        meal_id: int,
        current_user: ManagerDep,
        db: SessionDep
):
    return await delete_meal(db, meal_id)
