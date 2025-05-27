from fastapi import APIRouter

from app.ingredient.schema import IngredientCreate, IngredientRead, IngredientListResponse
from app.ingredient.crud import create_ingredient, get_ingredients, get_ingredient, delete_ingredient
from app.db.get_db import SessionDep
from app.auth.util import UserDep, ManagerDep

router = APIRouter()


@router.post("/", response_model=IngredientRead)
async def create_ingredient_endpoint(
        ingredient: IngredientCreate,
        current_user: ManagerDep,
        db: SessionDep
):
    db_ingredient = await create_ingredient(db, ingredient)
    return IngredientRead.model_validate(db_ingredient)


@router.get("/", response_model=IngredientListResponse)
async def get_ingredients_endpoint(
        current_user: UserDep,
        db: SessionDep,
        limit: int = 10,
        page: int = 1
):
    db_ingredients, total_count = await get_ingredients(db, limit, page)
    items = [IngredientRead.model_validate(ingredient) for ingredient in db_ingredients]
    return IngredientListResponse(total_count=total_count, items=items)


@router.get("/{ingredient_id}", response_model=IngredientRead)
async def get_ingredient_endpoint(
        ingredient_id: int,
        current_user: UserDep,
        db: SessionDep
):
    db_ingredient = await get_ingredient(db, ingredient_id)
    return IngredientRead.model_validate(db_ingredient)


@router.delete("/{ingredient_id}")
async def delete_ingredient_endpoint(
        ingredient_id: int,
        current_user: ManagerDep,
        db: SessionDep
):
    return await delete_ingredient(db, ingredient_id)
