from app.core import config


async def refresh_token_max_age(days: int | None = None) -> int:
    if not days or days <= 0:
        days = config.REFRESH_TOKEN_EXPIRE_DAYS

    return 60 * 60 * 24 * days
