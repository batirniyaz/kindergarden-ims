from datetime import date, datetime
from typing import Optional

from fastapi import APIRouter, Query

from app.db.get_db import SessionDep
from app.auth.util import AdminDep

from app.functions.uni_log import get_unified_logs
from app.schemas.uni_log import UnifiedLogResponse

router = APIRouter(prefix='/uni_log')


@router.get('/', response_model=UnifiedLogResponse)
async def unified_logs_endpoint(
        db: SessionDep,
        current_user: AdminDep,
        limit: int = Query(10, ge=1, le=100),
        page: int = Query(1, ge=1),
        user_id: Optional[int] = Query(None),
        log_type: Optional[str] = Query(None, regex="^(login_info|logging|change_log)$"),
        start_date: Optional[datetime] = Query(None),
        end_date: Optional[datetime] = Query(None)
):
    """
    Unified logs endpoint that aggregates data from login_info, logging, and change_log tables

    Query Parameters:
    - limit: Number of items per page (1-100, default: 10)
    - page: Page number (minimum: 1, default: 1)
    - user_id: Filter by specific user ID (optional)
    - log_type: Filter by log type - login_info, logging, or change_log (optional)
    - start_date: Filter logs from this date (ISO format, optional)
    - end_date: Filter logs until this date (ISO format, optional)

    Returns:
    - total_count: Total number of matching logs across all tables
    - items: Array of log entries with log_type field added
    """

    return await get_unified_logs(
        db=db,
        limit=limit,
        page=page,
        user_id=user_id,
        log_type=log_type,
        start_date=start_date,
        end_date=end_date
    )
