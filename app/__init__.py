from fastapi import APIRouter
from app.auth import router as auth_user_router
from app.celery.api import router as celery_router
from app.ingredient.api import router as ingredient_router
from app.meal.api import router as meal_router
from app.endpoints.meal_ingredient import router as meal_ingredient_router
from app.endpoints.serve_meal import router as serve_meal_router
from app.endpoints.delivery import router as delivery_router
from app.endpoints.portion_estimation import router as portion_estimation_router
from app.endpoints.notification import router as notification_router
from app.reports import router as report_router

router = APIRouter()

router.include_router(auth_user_router)
router.include_router(celery_router, prefix="/celery", tags=["Celery"])
router.include_router(ingredient_router, prefix="/ingredient", tags=["Ingredient"])
router.include_router(delivery_router, prefix="/delivery", tags=["Delivery"])
router.include_router(meal_router, prefix="/meal", tags=["Meal"])
router.include_router(meal_ingredient_router, prefix="/meal-ingredient", tags=["Meal Ingredient"])
router.include_router(serve_meal_router, prefix="/serve-meal", tags=["Serve Meal"])
router.include_router(portion_estimation_router, prefix="/ws/portion", tags=["Portion Estimation"])
router.include_router(notification_router, prefix="/ws/notification", tags=["Notification"])
router.include_router(report_router, prefix="/report", tags=["Report"])


from app.ingredient.schema import IngredientRead, IngredientShallow
from app.schemas.delivery import IngredientDeliveryRead
from app.meal.schema import MealRead, MealShallow
from app.schemas.meal_ingredient import MealIngredientRead
from app.schemas.serve_meal import ServeMealRead

IngredientRead.model_rebuild()
MealRead.model_rebuild()
MealIngredientRead.model_rebuild()
IngredientShallow.model_rebuild()
MealShallow.model_rebuild()
ServeMealRead.model_rebuild()
IngredientDeliveryRead.model_rebuild()