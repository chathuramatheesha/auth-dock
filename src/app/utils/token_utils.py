from app.core import config


async def get_refresh_token_max_age(days: int | None = None) -> int:
    if not days:
        days = config.REFRESH_TOKEN_EXPIRE_DAYS

    return 60 * 60 * 24 * days


async def get_refresh_token_expire_days(days: int | None = None) -> int:
    if not days:
        days = config.REFRESH_TOKEN_EXPIRE_DAYS
    return days


async def get_access_token_expire_minutes(minutes: int | None = None) -> int:
    if not minutes:
        minutes = config.ACCESS_TOKEN_EXPIRE_MINUTES
    return minutes
