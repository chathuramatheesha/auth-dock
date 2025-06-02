from typing import Annotated

from fastapi import Depends

from app.core import config
from ..services.jwt_service import JWTService


async def __get_jwt_service() -> JWTService:
    return JWTService(
        secret_key=config.SECRET_KEY,
        secret_key_access=config.SECRET_ACCESS_TOKEN,
        secret_key_refresh=config.SECRET_REFRESH_TOKEN,
        algorithm=config.ALGORITHM,
        access_expire=config.ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_expire=config.REFRESH_TOKEN_EXPIRE_DAYS,
        email_verification_expire=config.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES,
    )


JWTServiceDep = Annotated[JWTService, Depends(__get_jwt_service)]
