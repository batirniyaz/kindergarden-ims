
from app.changes.funcs import register_event_listener

from app.models.meal_ingredient import MealIngredient, Ingredient, Meal
from app.models.serve_meal import MealServing
from app.models.delivery import IngredientDelivery


def register_event_listeners():
    for model in [Meal, Ingredient, MealIngredient, MealServing, IngredientDelivery]:
        register_event_listener(model)
