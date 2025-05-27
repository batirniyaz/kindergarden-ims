from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.superuser import create_superuser
from app.db.base import create_db_and_tables
from app import router
from app.middleware.login_middleware import LoggingMiddleware


@asynccontextmanager
async def lifespan(main_app: FastAPI):
    await create_db_and_tables()
    await create_superuser()


    yield


app = FastAPI(
    title="Kindergarden Project",
    version="0.1",
    summary="Kindergarden Project API",
    lifespan=lifespan,
)


app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],)
app.add_middleware(LoggingMiddleware)


app.include_router(router)
