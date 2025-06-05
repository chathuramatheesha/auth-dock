from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.users.exceptions import UserNotFoundError
from .exceptions.auth_exceptions import (
    AuthTokenTypeInvalidError,
    AuthTokenRevokedError,
    AuthAccountDeletedError,
    AuthAccountDeactivatedError,
    AuthInvalidCredentialsError,
)
from .exceptions.token_exceptions import (
    JWTTokenCredentialsInvalidError,
    JWTTokenExpiredError,
    JWTTokenTypeInvalidError,
    JWTTokenInvalidError,
)


def auth_exception_handlers(app: FastAPI):
    @app.exception_handler(AuthInvalidCredentialsError)
    async def invalid_credentials_handler(
        request: Request,
        exc: AuthInvalidCredentialsError,
    ) -> JSONResponse:
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @app.exception_handler(AuthTokenTypeInvalidError)
    async def token_type_invalid_handler(
        request: Request,
        exc: AuthTokenTypeInvalidError,
    ) -> JSONResponse:
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(AuthTokenRevokedError)
    async def token_revoked_handler(
        request: Request,
        exc: AuthTokenRevokedError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(AuthAccountDeletedError)
    async def account_deleted_handler(
        request: Request,
        exc: AuthAccountDeletedError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(AuthAccountDeactivatedError)
    async def account_deactivated_handler(
        request: Request,
        exc: AuthAccountDeactivatedError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(
        request: Request,
        exc: UserNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(JWTTokenCredentialsInvalidError)
    async def jwt_credential_invalid_handler(
        request: Request,
        exc: JWTTokenCredentialsInvalidError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(JWTTokenExpiredError)
    async def jwt_expired_token_handler(
        request: Request,
        exc: JWTTokenExpiredError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(JWTTokenTypeInvalidError)
    async def jwt_token_type_invalid_handler(
        request: Request,
        exc: JWTTokenTypeInvalidError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(JWTTokenInvalidError)
    async def jwt_token_invalid_handler(
        request: Request,
        exc: JWTTokenInvalidError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=401,
            content={"detail": str(exc)},
            headers={"WWW-Authenticate": "Bearer"},
        )
