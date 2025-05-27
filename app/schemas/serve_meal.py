from pydantic import BaseModel, Field, ConfigDict
from typing import TYPE_CHECKING, Optional, List
import datetime

from app.schemas.util import TashkentBaseModel

if TYPE_CHECKING:
    from app.meal.schema import MealShallow


class ServeMealCreate(TashkentBaseModel):
    meal_id: int = Field(..., description="The ID of the meal")

    model_config = ConfigDict(extra='forbid')


class ServeMealRead(ServeMealCreate):
    id: int = Field(..., description="The ID of the meal serving")
    served_by: int = Field(..., description="The ID of the user who served the meal")
    created_at: datetime.datetime = Field(..., description="The timestamp when the meal was served")
    updated_at: datetime.datetime = Field(..., description="The timestamp when the meal serving was last updated")

    meal: Optional['MealShallow'] = Field(..., description="The meal containing the ingredient")

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, validate_assignment=True)


class ServeMealListResponse(TashkentBaseModel):
    total_count: int = Field(..., description="Total number of meal servings")
    meal_servings: List[ServeMealRead] = Field(..., description="List of meal servings")

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, validate_assignment=True)
