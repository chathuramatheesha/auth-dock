from typing import Annotated

from fastapi import Depends

from app.core import config
from app.utils.token_utils import (
    get_access_token_expire_minutes,
    get_refresh_token_expire_days,
)
from ..services.jwt_service import JWTService


async def __get_jwt_service() -> JWTService:
    return JWTService(
        secret_key=config.SECRET_KEY,
        secret_key_access=config.SECRET_ACCESS_TOKEN,
        secret_key_refresh=config.SECRET_REFRESH_TOKEN,
        algorithm=config.ALGORITHM,
        access_expire=await get_access_token_expire_minutes(),
        refresh_expire=await get_refresh_token_expire_days(),
        email_verification_expire=config.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES,
    )


JWTServiceDep = Annotated[JWTService, Depends(__get_jwt_service)]
