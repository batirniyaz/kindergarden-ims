from fastapi import APIRouter

from app.db.get_db import SessionDep
from app.auth.util import UserDep, CookDep

from app.schemas.serve_meal import ServeMealCreate, ServeMealRead, ServeMealListResponse
from app.functions.serve_meal import create_serve_meal, get_serve_meals

router = APIRouter()


@router.post("/", response_model=ServeMealRead)
async def create_serve_meal_endpoint(
        serve_meal: ServeMealCreate,
        current_user: CookDep,
        db: SessionDep
):
    db_serve_meal = await create_serve_meal(db, current_user, serve_meal)
    return ServeMealRead.model_validate(db_serve_meal)


@router.get('/', response_model=ServeMealListResponse)
async def get_serve_meals_endpoint(
        db: SessionDep,
        limit: int = 10,
        page: int = 1
):
    db_serve_meals, total_count = await get_serve_meals(db, limit, page)
    items = [ServeMealRead.model_validate(serve_meal) for serve_meal in db_serve_meals]
    return ServeMealListResponse(total_count=total_count, meal_servings=items)

