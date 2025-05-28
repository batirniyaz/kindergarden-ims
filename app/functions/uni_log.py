from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from datetime import datetime
from typing import Optional, List, Dict, Any
import asyncio

from app.auth.model import LoginInfo
from app.models.action_log import ActionLog
from app.changes.model import ChangeLog
from app.schemas.uni_log import UnifiedLogResponse


async def get_unified_logs(
        db: AsyncSession,
        limit: int = Query(10, ge=1, le=100),
        page: int = Query(1, ge=1),
        user_id: Optional[int] = Query(None),
        log_type: Optional[str] = Query(None, regex="^(login_info|logging|change_log)$"),
        start_date: Optional[datetime] = Query(None),
        end_date: Optional[datetime] = Query(None)
) -> UnifiedLogResponse:
    """
    Get unified logs from three different tables with filtering and pagination

    Args:
        db: Database session
        limit: Number of items per page
        page: Page number
        user_id: Filter by specific user ID
        log_type: Filter by log type (login_info, logging, change_log)
        start_date: Filter logs from this date
        end_date: Filter logs until this date

    Returns:
        UnifiedLogResponse with total_count and items
    """

    offset = (page - 1) * limit
    all_logs = []

    # Build queries for each table based on log_type filter
    queries_to_run = []

    if not log_type or log_type == "login_info":
        queries_to_run.append(("login_info", build_login_info_query))

    if not log_type or log_type == "logging":
        queries_to_run.append(("logging", build_logging_query))

    if not log_type or log_type == "change_log":
        queries_to_run.append(("change_log", build_change_log_query))

    # Execute all queries concurrently
    tasks = []
    for table_name, query_builder in queries_to_run:
        task = asyncio.create_task(
            execute_table_query(db, query_builder, user_id, start_date, end_date, table_name)
        )
        tasks.append(task)

    # Wait for all queries to complete
    results = await asyncio.gather(*tasks)

    # Combine all results
    for logs in results:
        all_logs.extend(logs)

    # Sort by datetime (using different datetime fields for each log type)
    all_logs.sort(key=lambda x: get_log_datetime(x), reverse=True)

    # Apply pagination
    total_count = len(all_logs)
    paginated_logs = all_logs[offset:offset + limit]

    return UnifiedLogResponse(
        total_count=total_count,
        items=paginated_logs
    )


def build_login_info_query(user_id: Optional[int], start_date: Optional[datetime], end_date: Optional[datetime]):
    """Build query for login_info table"""
    # Assuming your table model is LoginInfo
    query = select(LoginInfo)

    conditions = []

    if user_id:
        conditions.append(LoginInfo.user_id == user_id)

    if start_date:
        conditions.append(LoginInfo.login_at >= start_date)

    if end_date:
        conditions.append(LoginInfo.login_at <= end_date)

    if conditions:
        query = query.where(and_(*conditions))

    return query


def build_logging_query(user_id: Optional[int], start_date: Optional[datetime], end_date: Optional[datetime]):
    """Build query for logging table"""
    # Assuming your table model is ActivityLog
    query = select(ActionLog)

    conditions = []

    if user_id:
        conditions.append(ActionLog.user_id == user_id)

    if start_date:
        conditions.append(ActionLog.created_at >= start_date)

    if end_date:
        conditions.append(ActionLog.created_at <= end_date)

    if conditions:
        query = query.where(and_(*conditions))

    return query


def build_change_log_query(user_id: Optional[int], start_date: Optional[datetime], end_date: Optional[datetime]):
    """Build query for change_log table"""
    # Assuming your table model is ChangeLog
    query = select(ChangeLog)

    conditions = []

    if user_id:
        conditions.append(ChangeLog.user_id == user_id)

    if start_date:
        conditions.append(ChangeLog.created_at >= start_date)

    if end_date:
        conditions.append(ChangeLog.created_at <= end_date)

    if conditions:
        query = query.where(and_(*conditions))

    return query


async def execute_table_query(
        db: AsyncSession,
        query_builder,
        user_id: Optional[int],
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        table_name: str
) -> List[Dict[str, Any]]:
    """Execute query for a specific table and return formatted results"""

    query = query_builder(user_id, start_date, end_date)
    result = await db.execute(query)
    rows = result.scalars().all()

    # Convert to dictionary format with log_type added
    formatted_logs = []
    for row in rows:
        log_dict = {}

        if table_name == "login_info":
            log_dict = {
                "id": row.id,
                "user_id": row.user_id,
                "email": row.email,
                "phone": row.phone,
                "username": row.username,
                "login_at": row.login_at,
                "log_type": "login_info"
            }

        elif table_name == "logging":
            log_dict = {
                "id": row.id,
                "user_id": row.user_id,
                "phone": row.phone,
                "email": row.email,
                "username": row.username,
                "role": row.role,
                "query": row.query,
                "method": row.method,
                "path": row.path,
                "status_code": row.status_code,
                "process_time": row.process_time,
                "client_host": row.client_host,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "log_type": "logging"
            }

        elif table_name == "change_log":
            log_dict = {
                "id": row.id,
                "user_id": row.user_id,
                "table_name": row.table_name,
                "operation": row.operation,
                "before_data": row.before_data,
                "after_data": row.after_data,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
                "log_type": "change_log"
            }

        formatted_logs.append(log_dict)

    return formatted_logs


def get_log_datetime(log: Dict[str, Any]) -> datetime:
    """Extract datetime from log entry based on log type"""
    log_type = log.get("log_type")

    if log_type == "login_info":
        return log.get("login_at")
    elif log_type == "logging":
        return log.get("created_at")
    elif log_type == "change_log":
        return log.get("created_at")

    # Fallback
    return datetime.min