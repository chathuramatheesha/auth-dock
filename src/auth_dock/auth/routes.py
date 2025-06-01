from fastapi import APIRouter, status

from .dependencies import AuthServiceDep
from .schemas import UserCreateIn, UserPublicOut
from ..users.dtos import UserCreateInDTO
from ..utils.dto_utils import pydantic_to_dto

router = APIRouter()


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
)
async def signup(user_create: UserCreateIn, service: AuthServiceDep) -> UserPublicOut:
    return await service.register_user(
        await pydantic_to_dto(user_create, UserCreateInDTO)
    )


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
)
async def login():
    pass


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
)
async def logout():
    pass
