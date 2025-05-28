import datetime

from pydantic import BaseModel, Field, ConfigDict
from typing import List, TYPE_CHECKING, Optional

from app.schemas.util import TashkentBaseModel

if TYPE_CHECKING:
    from app.schemas.meal_ingredient import MealIngredientRead


class MealCreate(TashkentBaseModel):
    name: str = Field(..., max_length=255, description="The name of the meal")

    model_config = ConfigDict(extra='forbid')


class MealRead(MealCreate):
    id: int = Field(..., description="The ID of the meal")
    created_at: datetime.datetime = Field(..., description="The time the meal was created")
    updated_at: datetime.datetime = Field(..., description="The time the meal was updated")

    added_by: Optional[int] = Field(None, description="The ID of the user who added the meal")
    ingredients: List['MealIngredientRead'] = Field(default_factory=list, description="List of ingredients in the meal")

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, validate_assignment=True)


class MealListResponse(TashkentBaseModel):
    total_count: int = Field(..., description="Total number of meals")
    items: List[MealRead] = Field(..., description="List of meals")

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, validate_assignment=True)


class MealShallow(TashkentBaseModel):
    id: int = Field(..., description="The ID of the meal")
    name: str = Field(..., max_length=255, description="The name of the meal")
    created_at: datetime.datetime = Field(..., description="The time the meal was created")
    updated_at: datetime.datetime = Field(..., description="The time the meal was updated")

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, validate_assignment=True)