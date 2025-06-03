from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.orm import DeclarativeBase

from app.core import config


class Base(DeclarativeBase, AsyncAttrs):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)" "s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


async_engine = create_async_engine(config.DATABASE_URL, echo=config.DATABASE_ECHO)
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
)
