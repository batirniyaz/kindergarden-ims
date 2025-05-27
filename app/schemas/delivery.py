import datetime

from pydantic import BaseModel, Field, ConfigDict
from typing import TYPE_CHECKING, List, Optional

from app.ingredient.schema import IngredientShallow
from app.auth.schema import UserRead
from app.schemas.util import TashkentBaseModel


class IngredientDeliveryCreate(TashkentBaseModel):
    ingredient_id: int = Field(..., description="The ID of the ingredient")
    weight: float = Field(..., gt=0, description="The weight in grams of the ingredient delivered")

    model_config = ConfigDict(extra='forbid')


class IngredientDeliveryRead(IngredientDeliveryCreate):
    id: int = Field(..., description="The ID of the ingredient delivery")
    accepted: int = Field(..., description="The accepted staff of the ingredient delivery")
    created_at: datetime.datetime = Field(..., description="The time the ingredient was delivered")
    updated_at: datetime.datetime = Field(..., description="The time the ingredient delivery was updated")

    ingredient: Optional[IngredientShallow] = Field(..., description="The ingredient associated with the delivery")
    user: Optional[UserRead] = Field(..., description="The user who accepted the delivery")
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, validate_assignment=True)


class IngredientDeliveryListResponse(TashkentBaseModel):
    total_count: int = Field(..., description="Total number of ingredient deliveries")
    items: List[IngredientDeliveryRead] = Field(..., description="List of ingredient deliveries")

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, validate_assignment=True)
