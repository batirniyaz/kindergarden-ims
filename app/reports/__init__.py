from fastapi import APIRouter

from app.reports.ingredient_usage import router as ingredient_usage_router
from app.reports.monthly_summary import router as monthly_summary_router
from app.reports.ingredient_analysis import router as ingredient_analysis_router

router = APIRouter()

router.include_router(ingredient_usage_router, prefix="/ingredient-usage")
router.include_router(monthly_summary_router, prefix="/monthly-summary")
router.include_router(ingredient_analysis_router, prefix="/ingredient-analysis")