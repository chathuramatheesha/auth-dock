from fastapi import APIRouter, status, Request, Response

from app.utils.dto_utils import pydantic_to_dto
from .dependencies import AuthServiceDep, AuthTokenDep, AuthCurrentUserDep
from .schemas import AuthSignUpIn, UserPublicOut, AuthLoginIn, AuthTokenOut
from ..schemas import MessageOut
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
    return await service.login(request, response, user_login_reqeust)


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
async def logout(
    request: Request,
    response: Response,
    token: AuthTokenDep,
    current_user: AuthCurrentUserDep,
    service: AuthServiceDep,
) -> MessageOut:
    return await service.logout(request, response, current_user, token)
