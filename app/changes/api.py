from fastapi import APIRouter

from app.changes.funcs import get_changes_log
from app.db.get_db import SessionDep
from app.auth.util import AdminDep

router = APIRouter(prefix='/change_log')


@router.get("/")
async def get_changes_log_endpoint(
        current_user: AdminDep,
        db: SessionDep,
        limit: int = 10,
        page: int = 1,
):
    return await get_changes_log(db, limit, page)