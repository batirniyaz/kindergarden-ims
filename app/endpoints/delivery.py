from fastapi import APIRouter

from app.auth.util import UserDep
from app.db.get_db import SessionDep
from app.functions.delivery import create_delivery, get_deliveries, get_delivery, delete_delivery
from app.schemas.delivery import IngredientDeliveryRead, IngredientDeliveryCreate, IngredientDeliveryListResponse

router = APIRouter()


@router.post("/", response_model=IngredientDeliveryRead)
async def create_delivery_endpoint(
        delivery: IngredientDeliveryCreate,
        current_user: UserDep,
        db: SessionDep
):
    db_delivery = await create_delivery(db, current_user, delivery)
    return IngredientDeliveryRead.model_validate(db_delivery)


@router.get("/", response_model=IngredientDeliveryListResponse)
async def get_deliveries_endpoint(
        db: SessionDep,
        current_user: UserDep,
        limit: int = 10,
        page: int = 1,
):
    deliveries, total_count = await get_deliveries(db, limit, page)
    items = [IngredientDeliveryRead.model_validate(delivery) for delivery in deliveries]
    return IngredientDeliveryListResponse(total_count=total_count, items=items)


@router.get("/{delivery_id}", response_model=IngredientDeliveryRead)
async def get_delivery_endpoint(
        delivery_id: int,
        db: SessionDep,
        current_user: UserDep
):
    db_delivery = await get_delivery(db, delivery_id)
    return IngredientDeliveryRead.model_validate(db_delivery)


@router.delete("/{delivery_id}")
async def delete_delivery_endpoint(
        delivery_id: int,
        db: SessionDep,
        current_user: UserDep
):
    return await delete_delivery(db, delivery_id)

