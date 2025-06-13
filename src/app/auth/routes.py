from fastapi import APIRouter, status, Request, Response, Cookie

from app.common.schemas import MessageOut
from app.users.dtos import UserCreateInDTO
from app.utils.dto_utils import pydantic_to_dto
from app.utils.token_utils import get_refresh_token_max_age
from .dependencies import AuthServiceDep, AuthTokenDep, AuthCurrentUserDep
from .dtos import AuthLoginInDTO
from .dtos.auth_dtos import RefreshAccessTokenInDTO
from .enums import TokenType
from .schemas import AuthSignUpIn, UserPublicOut, AuthLoginIn, AuthTokenOut

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
    refresh_token: str | None = Cookie(None),
) -> AuthTokenOut:
    async def access_token(header: str) -> str | None:
        if not header:
            return None

        return header.split(" ")[1]

    tokens = await service.login(
        AuthLoginInDTO(
            email=str(user_login_reqeust.email),
            password=user_login_reqeust.password,
            ip_address=request.client.host,
            previous_access_token=await access_token(
                request.headers.get("Authorization")
            ),
            previous_refresh_token=refresh_token,
            device_info=request.headers.get("user-agent"),
        )
    )
    response.set_cookie(
        key=TokenType.REFRESH_TOKEN.value,
        value=tokens.refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        path="/api/v1/auth",
        max_age=await get_refresh_token_max_age(),
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
    )


@router.post("/refresh-token", status_code=status.HTTP_200_OK)
async def refresh_access_token(
    request: Request,
    response: Response,
    token: AuthTokenDep,
    service: AuthServiceDep,
    refresh_token: str = Cookie(Ellipsis),
) -> AuthTokenOut:
    tokens = await service.refresh_access_token(
        RefreshAccessTokenInDTO(
            access_token=token.credentials,
            refresh_token=refresh_token,
            ip_address=request.client.host,
            device_info=request.headers.get("user-agent"),
        )
    )

    if tokens.refresh_token:
        response.set_cookie(
            key=TokenType.REFRESH_TOKEN.value,
            value=tokens.refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            path="/api/v1/auth",
            max_age=await get_refresh_token_max_age(),
        )

    return tokens
