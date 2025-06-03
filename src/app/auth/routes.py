from fastapi import APIRouter, status, Request, Response

from app.users.dtos import UserCreateInDTO
from app.utils.dto_utils import pydantic_to_dto
from app.utils.token_utils import refresh_token_max_age
from .dependencies import AuthServiceDep, AuthTokenDep, AuthCurrentUserDep
from .dtos import AuthLoginInDTO
from .enums import TokenType
from .schemas import AuthSignUpIn, UserPublicOut, AuthLoginIn, AuthTokenOut
from ..schemas import MessageOut

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
    response.delete_cookie(TokenType.REFRESH_TOKEN.value)
    tokens = await service.login(
        AuthLoginInDTO(
            email=str(user_login_reqeust.email),
            password=user_login_reqeust.password,
            ip_address=request.client.host,
            previous_refresh_token=request.cookies.get(TokenType.REFRESH_TOKEN.value),
            device_info=request.headers.get("user-agent"),
        )
    )
    response.set_cookie(
        key=TokenType.REFRESH_TOKEN.value,
        value=tokens.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/refresh-token",
        max_age=await refresh_token_max_age(),
    )

    return tokens


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
async def logout(
    request: Request,
    token: AuthTokenDep,
    current_user: AuthCurrentUserDep,
    service: AuthServiceDep,
) -> MessageOut:
    refresh_token = request.cookies.get(TokenType.REFRESH_TOKEN.value)
    return await service.logout(
        access_token=token.credentials,
        refresh_token=refresh_token,
        current_user=current_user,
    )
