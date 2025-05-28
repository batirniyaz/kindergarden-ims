import asyncio
from contextvars import ContextVar
from enum import Enum
from typing import Type, Optional
from datetime import datetime, timezone, timedelta

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.event import listens_for
from app.changes.model import ChangeLog, OperationType
from app.db.get_db import get_async_session
from sqlalchemy.orm.attributes import get_history
from sqlalchemy.orm.session import Session

log_queue = asyncio.Queue()


current_user_id: ContextVar[Optional[int]] = ContextVar('current_user_id', default=None)


def set_current_user(user_id: int):
    """Set the current user ID in context"""
    current_user_id.set(user_id)


def get_current_user() -> Optional[int]:
    """Get the current user ID from context"""
    user_id = current_user_id.get()
    return user_id


def serialize(data):
    if data is None:
        return None
    return {
        key: (
            value.astimezone(timezone(timedelta(hours=5))).isoformat()
            if isinstance(value, datetime)
            else value.value if isinstance(value, Enum)
            else value
        )
        for key, value in data.items()
    }


async def log_change(db: AsyncSession, table_name: str, operation: OperationType, user_id: int, before_data: dict, after_data: dict):
    try:
        change_log = ChangeLog(
            table_name=table_name,
            operation=operation,
            before_data=serialize(before_data),
            after_data=serialize(after_data),
            user_id=user_id,
        )
        db.add(change_log)
        await db.commit()
        await db.refresh(change_log)
    except Exception as e:
        await db.rollback()
        raise e


async def process_log_queue():
    async for db_session in get_async_session():
        while True:
            table_name, operation, user_id, before_data, after_data = await log_queue.get()
            try:
                await log_change(db_session, table_name, operation, user_id, before_data, after_data)
            except Exception as e:
                print(f"Failed to log change: {e}")
            finally:
                log_queue.task_done()


def register_event_listener(model: Type):

    @listens_for(Session, 'before_flush')
    def capture_before_flush(session, flush_context, instances):
        for instance in session.dirty:
            if isinstance(instance, model):
                original_values = {}
                for column in instance.__table__.columns:
                    try:
                        history = get_history(instance, column.key)
                        if history.has_changes():
                            original_values[column.key] = history.deleted[0] if history.deleted else None
                    except Exception as e:
                        print(f"Error capturing original value for {column.key}: {e}")

                if original_values:
                    setattr(instance, '_original_values', original_values)

    @listens_for(model, 'after_update')
    def receive_after_update(mapper, connection, target):
        db_session = AsyncSession.object_session(target)
        if db_session:
            before_data = getattr(target, '_original_values', {})
            changed_attrs = [attr for attr in mapper.columns if get_history(target, attr.key).has_changes()]
            after_data = {
                attr.key: getattr(target, attr.key)
                for attr in changed_attrs
                if attr.key != 'updated_at'
            }

            if after_data:
                user_id = get_current_user()

                loop = asyncio.get_event_loop()
                asyncio.run_coroutine_threadsafe(
                    log_queue.put((target.__tablename__, OperationType.UPDATE, user_id,
                                   before_data, after_data)),
                    loop
                )


            if hasattr(target, '_original_values'):
                delattr(target, '_original_values')

    @listens_for(model, 'after_insert')
    def receive_after_insert(mapper, connection, target):
        db_session = AsyncSession.object_session(target)
        if db_session:
            user_id = get_current_user()
            asyncio.create_task(
                log_queue.put((
                    target.__tablename__,
                    OperationType.CREATE,
                    user_id,
                    None,
                    {column.key: getattr(target, column.key) for column in mapper.columns},
                ))
            )

    @listens_for(model, 'after_delete')
    def receive_after_delete(mapper, connection, target):
        db_session = AsyncSession.object_session(target)
        if db_session:
            user_id = get_current_user()
            asyncio.create_task(
                log_queue.put((target.__tablename__, OperationType.DELETE, user_id,
                               {column.key: getattr(target, column.key) for column in mapper.columns},
                               None))
            )


async def get_changes_log(db, limit: int = 10, page: int = 1):
    try:
        result = await db.execute(select(ChangeLog).order_by(ChangeLog.created_at.desc()).limit(limit).offset((page - 1) * limit))
        changes = result.scalars().all()

        total_count = await db.scalar(select(func.count(ChangeLog.id)))

        return {"data": changes if changes else [], "total_count": total_count}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))