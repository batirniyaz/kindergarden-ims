from pydantic import BaseModel, Field, ConfigDict
from typing import TYPE_CHECKING, Optional, List

from app.schemas.util import TashkentBaseModel

if TYPE_CHECKING:
    from app.ingredient.schema import IngredientShallow
    from app.meal.schema import MealShallow


class MealIngredientCreate(TashkentBaseModel):
    meal_id: int = Field(..., description="The ID of the meal")
    ingredient_id: int = Field(..., description="The ID of the ingredient")
    weight: float = Field(..., gt=0, description="The weight in grams of the ingredient in the meal")

    model_config = ConfigDict(extra='forbid')


class MealIngredientUpdate(TashkentBaseModel):
    weight: float = Field(..., gt=0, description="The weight in grams of the ingredient in the meal")


class MealIngredientRead(MealIngredientCreate):

    ingredient: Optional['IngredientShallow'] = Field(..., description="The ingredient in the meal")
    meal: Optional['MealShallow'] = Field(..., description="The meal containing the ingredient")

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, validate_assignment=True)


class MealIngredientListResponse(TashkentBaseModel):
    total_count: int = Field(..., description="Total number of meal ingredients")
    meal_ingredients: List[MealIngredientRead] = Field(..., description="List of meal ingredients")

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, validate_assignment=True)
