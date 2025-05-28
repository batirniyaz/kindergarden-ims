import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.superuser import create_superuser
from app.changes.funcs import process_log_queue
from app.db.base import create_db_and_tables
from app import router
from app.middleware.login_middleware import LoggingMiddleware
from app.changes.track_models import register_event_listeners


@asynccontextmanager
async def lifespan(main_app: FastAPI):
    await create_db_and_tables()
    await create_superuser()
    register_event_listeners()
    log_queue_task = asyncio.create_task(process_log_queue())

    try:
        yield
    finally:
        log_queue_task.cancel()
        try:
            await log_queue_task
        except asyncio.CancelledError:
            pass


app = FastAPI(
    title="Kindergarden Project",
    version="0.1",
    summary="Kindergarden Project API",
    lifespan=lifespan,
)


app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)
app.add_middleware(LoggingMiddleware)


app.include_router(router)
