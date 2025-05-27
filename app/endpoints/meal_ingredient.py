from fastapi import APIRouter

from app.db.get_db import SessionDep
from app.auth.util import UserDep, ManagerDep

from app.schemas.meal_ingredient import MealIngredientCreate, MealIngredientRead, MealIngredientUpdate, MealIngredientListResponse
from app.functions.meal_ingredient import create_meal_ingredient, get_meal_ingredients, get_meal_ingredient, update_meal_ingredient, delete_meal_ingredient

router = APIRouter()


@router.post("/", response_model=MealIngredientRead)
async def create_meal_ingredient_endpoint(
        meal_ingredient: MealIngredientCreate,
        current_user: ManagerDep,
        db: SessionDep
):
    db_meal_ingredient = await create_meal_ingredient(db, meal_ingredient)
    return MealIngredientRead.model_validate(db_meal_ingredient)


@router.get("/", response_model=MealIngredientListResponse)
async def get_meal_ingredients_endpoint(
        current_user: UserDep,
        db: SessionDep,
        limit: int = 10,
        page: int = 1
):
    db_meal_ingredients, total_count = await get_meal_ingredients(db, limit, page)
    items = [MealIngredientRead.model_validate(meal_ingredient) for meal_ingredient in db_meal_ingredients]
    return MealIngredientListResponse(total_count=total_count, meal_ingredients=items)


@router.get("/{meal_id}/{ingredient_id}", response_model=MealIngredientRead)
async def get_meal_ingredient_endpoint(
        meal_id: int,
        ingredient_id: int,
        current_user: UserDep,
        db: SessionDep
):
    db_meal_ingredient = await get_meal_ingredient(db, meal_id, ingredient_id)
    return MealIngredientRead.model_validate(db_meal_ingredient)


@router.put("/{meal_id}/{ingredient_id}", response_model=MealIngredientRead)
async def update_meal_ingredient_endpoint(
        meal_id: int,
        ingredient_id: int,
        meal_ingredient: MealIngredientUpdate,
        current_user: ManagerDep,
        db: SessionDep
):
    db_meal_ingredient = await update_meal_ingredient(db, meal_id, ingredient_id, meal_ingredient)
    return MealIngredientRead.model_validate(db_meal_ingredient)


@router.delete("/{meal_id}/{ingredient_id}")
async def delete_meal_ingredient_endpoint(
        meal_id: int,
        ingredient_id: int,
        current_user: ManagerDep,
        db: SessionDep
):
    return await delete_meal_ingredient(db, meal_id, ingredient_id)
