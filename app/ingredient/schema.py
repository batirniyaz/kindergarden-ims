import datetime

from pydantic import BaseModel, Field, ConfigDict
from typing import TYPE_CHECKING, List

from app.schemas.util import TashkentBaseModel

if TYPE_CHECKING:
    from app.schemas.meal_ingredient import MealIngredientRead


class IngredientCreate(TashkentBaseModel):
    name: str = Field(..., max_length=255, description="The name of the ingredient")

    model_config = ConfigDict(extra='forbid')


class IngredientRead(IngredientCreate):
    id: int = Field(..., description="The ID of the ingredient")
    weight: float = Field(..., ge=0, description="The weight in grams of the ingredient")
    created_at: datetime.datetime = Field(..., description="The time the ingredient was created")
    updated_at: datetime.datetime = Field(..., description="The time the ingredient was updated")

    meals: List['MealIngredientRead'] = Field(default_factory=list, description="List of meals containing the ingredient")

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, validate_assignment=True)


class IngredientListResponse(TashkentBaseModel):
    total_count: int = Field(..., description="Total number of ingredients")
    items: List[IngredientRead] = Field(..., description="List of ingredients")

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, validate_assignment=True)


class IngredientShallow(TashkentBaseModel):
    id: int = Field(..., description="The ID of the ingredient")
    name: str = Field(..., max_length=255, description="The name of the ingredient")
    weight: float = Field(..., gt=0, description="The weight in grams of the ingredient")
    created_at: datetime.datetime = Field(..., description="The time the ingredient was created")
    updated_at: datetime.datetime = Field(..., description="The time the ingredient was updated")

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, validate_assignment=True)
