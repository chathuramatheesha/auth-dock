from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone, timedelta

import ulid
from jose import jwt, ExpiredSignatureError
from jose.exceptions import JWTError

from ..dtos import JWTAccessTokenDTO, JWTRefreshTokenDTO, JWTEmailTokenDTO
from ..enums import TokenType
from ..exceptions.token_exceptions import (
    JWTTokenTypeInvalidError,
    JWTTokenInvalidError,
    JWTTokenExpiredError,
    JWTTokenCredentialsInvalidError,
)


class JWTService:
    def __init__(
        self,
        secret_key: str,
        secret_key_access: str,
        secret_key_refresh: str,
        algorithm: str,
        access_expire: int,
        refresh_expire: int,
        email_verification_expire: int,
    ) -> None:
        self.__secret_key = secret_key
        self.__secret_key_access = secret_key_access
        self.__secret_key_refresh = secret_key_refresh
        self.__algorithm = algorithm
        self.__access_expire_minutes = access_expire
        self.__refresh_expire_days = refresh_expire
        self.__email_verification_expire_minutes = email_verification_expire

    async def encode_token(
        self,
        user_id: str,
        token_type: TokenType,
        **extra_fields,
    ) -> str:
        expires_at = datetime.now(timezone.utc)

        if token_type == TokenType.ACCESS_TOKEN:
            secret_key = self.__secret_key_access
            dto_class = JWTAccessTokenDTO
            expires_at += timedelta(minutes=self.__access_expire_minutes)
        elif token_type == TokenType.REFRESH_TOKEN:
            secret_key = self.__secret_key_refresh
            dto_class = JWTRefreshTokenDTO
            expires_at += timedelta(days=self.__refresh_expire_days)
        elif token_type == TokenType.EMAIL_TOKEN:
            secret_key = self.__secret_key
            dto_class = JWTEmailTokenDTO
            expires_at += timedelta(minutes=self.__email_verification_expire_minutes)
        else:
            raise JWTTokenTypeInvalidError(token_type, [item for item in TokenType])

        if not is_dataclass(dto_class):
            raise TypeError(f"{dto_class} must be a dataclass")

        payload = dto_class(
            sub=user_id,
            jti=str(ulid.new()),
            iat=datetime.now(timezone.utc),
            exp=expires_at,
            type=token_type,
            **extra_fields,
        )
        return jwt.encode(asdict(payload), key=secret_key, algorithm=self.__algorithm)

    async def decode_token(
        self,
        token: str,
        token_type: TokenType,
        verify_sub: bool = True,
        verify_jti: bool = True,
        verify_exp: bool = True,
    ) -> JWTAccessTokenDTO | JWTRefreshTokenDTO | JWTEmailTokenDTO:
        if not token:
            raise JWTTokenInvalidError()

        try:
            if token_type == TokenType.ACCESS_TOKEN:
                secret_key = self.__secret_key_access
                dto_class = JWTAccessTokenDTO
            elif token_type == TokenType.REFRESH_TOKEN:
                secret_key = self.__secret_key_refresh
                dto_class = JWTRefreshTokenDTO
            elif token_type == TokenType.EMAIL_TOKEN:
                secret_key = self.__secret_key
                dto_class = JWTEmailTokenDTO
            else:
                raise JWTTokenTypeInvalidError(token_type, [item for item in TokenType])

            payload = jwt.decode(
                token,
                key=secret_key,
                algorithms=[self.__algorithm],
                options={"verify_exp": verify_exp},
            )

            payload_token_type = payload.get("type")

            if not payload_token_type or payload_token_type != token_type:
                raise JWTTokenTypeInvalidError(payload_token_type, [token_type])

            if token_type == TokenType.REFRESH_TOKEN and not payload.get("ip"):
                raise JWTTokenInvalidError()

            if not is_dataclass(dto_class):
                raise TypeError(f"{dto_class} must be a dataclass")

            token_obj = dto_class(**payload)
            checks = {
                "sub": verify_sub,
                "jti": verify_jti,
                "exp": verify_exp,
                "iat": True,
            }

            for attr, should_verify in checks.items():
                if should_verify and not getattr(token_obj, attr, None):
                    raise JWTTokenInvalidError()

            expires_at = payload.get("exp")
            issued_at = payload.get("iat")

            token_obj.exp = datetime.fromtimestamp(expires_at, tz=timezone.utc)
            token_obj.iat = datetime.fromtimestamp(issued_at, tz=timezone.utc)

            return token_obj

        except ExpiredSignatureError:
            raise JWTTokenExpiredError()

        except JWTError:
            raise JWTTokenCredentialsInvalidError()
