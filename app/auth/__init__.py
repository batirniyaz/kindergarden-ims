from fastapi import APIRouter
from app.auth.api import router as auth_router
from app.auth.endpoint import router as user_router
from app.changes.api import router as changes_router
from app.endpoints.uni_log import router as uni_log

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(changes_router, prefix="/auth", tags=["Auth"])
router.include_router(uni_log, prefix="/auth", tags=["Auth"])
router.include_router(user_router, prefix="/user", tags=["User"])
