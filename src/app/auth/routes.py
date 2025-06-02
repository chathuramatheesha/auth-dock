from fastapi import APIRouter, status, Request, Response

from app.utils.dto_utils import pydantic_to_dto
from app.utils.token_utils import refresh_token_max_age
from .dependencies import AuthServiceDep
from .enums import TokenType
from .schemas import AuthSignUpIn, UserPublicOut, AuthLoginIn, AuthTokenOut
from ..users.dtos import UserCreateInDTO

router = APIRouter()


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user_create: AuthSignUpIn, service: AuthServiceDep) -> UserPublicOut:
    return await service.signup(await pydantic_to_dto(user_create, UserCreateInDTO))


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    response: Response,
    user_login_reqeust: AuthLoginIn,
    service: AuthServiceDep,
) -> AuthTokenOut:
    tokens = await service.login(request, user_login_reqeust)
    response.set_cookie(
        key=TokenType.REFRESH_TOKEN.value,
        value=tokens.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=refresh_token_max_age(),
    )
    return tokens


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
async def logout():
    pass
