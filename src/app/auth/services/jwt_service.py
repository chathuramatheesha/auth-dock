from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone, timedelta

import ulid
from jose import jwt, JWTError

from ..dtos import JWTAccessTokenDTO, JWTRefreshTokenDTO, JWTEmailTokenDTO
from ..enums import TokenType
from ..exceptions import token_exceptions


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
        self, user_id: str, token_type: TokenType, **extra_fields
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
            raise token_exceptions.jwt_token_invalid_type_exception

        if not is_dataclass(dto_class):
            raise TypeError(f"{dto_class} must be a dataclass")

        payload = dto_class(
            sub=user_id,
            jti=str(ulid.new()),
            iat=datetime.now(timezone.utc),
            exp=expires_at,
            **extra_fields,
        )
        return jwt.encode(asdict(payload), key=secret_key, algorithm=self.__algorithm)

    async def decode_token(
        self,
        token: str,
        token_type: TokenType,
        verify_token: bool = True,
    ) -> JWTAccessTokenDTO | JWTRefreshTokenDTO | JWTEmailTokenDTO:
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
                raise token_exceptions.jwt_token_invalid_type_exception

            payload = jwt.decode(token, key=secret_key, algorithms=[self.__algorithm])

            if not is_dataclass(dto_class):
                raise TypeError(f"{dto_class} must be a dataclass")

            token_obj = dto_class(**payload)

            if (
                not token_obj.jti
                or not token_obj.sub
                or not token_obj.exp
                or not token_obj.iat
            ):
                raise token_exceptions.jwt_token_invalid_exception

            current_datetime = datetime.now(timezone.utc)
            expires_at = payload.get("exp")
            issued_at = payload.get("iat")

            if not expires_at or not issued_at:
                raise token_exceptions.jwt_token_invalid_exception

            token_obj.exp = datetime.fromtimestamp(expires_at, tz=timezone.utc)
            token_obj.iat = datetime.fromtimestamp(issued_at, tz=timezone.utc)

            if not token_obj.exp or token_obj.exp < current_datetime:
                raise token_exceptions.jwt_token_expired_exception

            return token_obj

        except JWTError:
            raise token_exceptions.jwt_credentials_exception

    async def decode_refresh_token_ignore_exceptions(
        self, token: str
    ) -> JWTRefreshTokenDTO | None:
        try:
            payload = jwt.decode(
                token, key=self.__secret_key_refresh, algorithms=[self.__algorithm]
            )
            token_obj = JWTRefreshTokenDTO(**payload)

            if (
                not token_obj.jti
                or not token_obj.sub
                or not token_obj.exp
                or not token_obj.iat
            ):
                raise None

            expires_at = payload.get("exp")
            issued_at = payload.get("iat")

            if not expires_at or not issued_at:
                raise None

            token_obj.exp = datetime.fromtimestamp(expires_at, tz=timezone.utc)
            token_obj.iat = datetime.fromtimestamp(issued_at, tz=timezone.utc)

            if not token_obj.exp:
                raise None

            return token_obj

        except JWTError:
            return None
