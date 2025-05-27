from datetime import timedelta

from sqlalchemy import delete

from app.celery.celery_app import celery_app
import time
import asyncio

from app.config import now_tashkent
from app.db.db import async_session_maker
from app.models.action_log import ActionLog
from app.reports.ingredient_usage import get_ingredient_usage_over_time
from app.reports.monthly_summary import get_monthly_summary_report



@celery_app.task
def test_task(name: str):
    time.sleep(3)
    return f"Hello, {name}!"


def run_async(func):
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper


@celery_app.task(name="tasks.logs.delete_old_logs")
def delete_old_logs():
    return run_async(_delete_old_logs)()


async def _delete_old_logs():
    async with async_session_maker() as session:
        threshold = now_tashkent() - timedelta(days=30)
        await session.execute(delete(ActionLog).where(ActionLog.created_at < threshold))
        await session.commit()


@celery_app.task(name="tasks.generate_ingredient_usage")
def generate_ingredient_usage(params):
    async def _wrapped():
        return await _generate_ingredient_usage(params)

    return run_async(_wrapped)()


async def _generate_ingredient_usage(params):
    async with async_session_maker() as db:
        data = await get_ingredient_usage_over_time(db, **params)
        return data


@celery_app.task(name="tasks.generate_monthly_summary")
def generate_monthly_summary(params):
    async def _wrapped():
        return await _generate_monthly_summary(params)

    return run_async(_wrapped)()


async def _generate_monthly_summary(params):
    async with async_session_maker() as db:
        data = await get_monthly_summary_report(db, **params)
        return data
