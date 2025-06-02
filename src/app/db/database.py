from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase

from app.core import config


class Base(DeclarativeBase, AsyncAttrs):
    pass


async_engine = create_async_engine(config.DATABASE_URL, echo=True)
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
)
