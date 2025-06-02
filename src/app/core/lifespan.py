from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.init import init_db
from .logging_conf import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    await configure_logging()
    await init_db()
    yield
    print("Server is shutting down...")
