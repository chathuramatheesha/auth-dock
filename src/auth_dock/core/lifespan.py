from contextlib import asynccontextmanager

from fastapi import FastAPI

from auth_dock.db.init import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    print("Server is shutting down...")
