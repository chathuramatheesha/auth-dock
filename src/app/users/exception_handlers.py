from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse, Response

from . import constants
from .exceptions import (
    UserEmailExistsError,
    UserEmailNotFoundError,
    UserIDNotFoundError,
    UserNotFoundError,
    UserCreateFailedError,
    UserUpdateFailedError,
)


def add_user_exception_handlers(app: FastAPI):
    @app.exception_handler(UserEmailExistsError)
    async def email_exists_handler(
        request: Request,
        exc: UserEmailExistsError,
    ) -> Response:
        return JSONResponse(
            status_code=409,
            content={
                "detail": constants.ERR_USER_EMAIL_ALREADY_EXISTS.format(
                    email=exc.email
                )
            },
        )

    @app.exception_handler(UserEmailNotFoundError)
    async def email_not_found_handler(
        request: Request,
        exc: UserEmailNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": exc.email},
        )

    @app.exception_handler(UserIDNotFoundError)
    async def id_not_found_handler(
        request: Request,
        exc: UserIDNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"detail": str(exc)},
        )

    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(
        request: Request,
        exc: UserNotFoundError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={
                "detail": str(exc),
            },
        )

    @app.exception_handler(UserCreateFailedError)
    async def create_failed_handler(
        request: Request,
        exc: UserCreateFailedError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)},
        )

    @app.exception_handler(UserUpdateFailedError)
    async def update_failed_handler(
        request: Request,
        exc: UserUpdateFailedError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content={"detail": {exc}},
        )
