from dataclasses import asdict

import pytest
from httpx import AsyncClient

from app.users.constants import ERR_USER_EMAIL_ALREADY_EXISTS
from tests.dtos import UserRegisterDTO
from tests.routers.auth import auth_base_url

pytestmark = pytest.mark.anyio
base_url = f"{auth_base_url}/signup"


async def test_register_user_success(
    async_client: AsyncClient, new_random_user: UserRegisterDTO
):
    response = await async_client.post(base_url, json={**asdict(new_random_user)})
    data: dict = response.json()

    assert response.status_code == 201
    assert {
        "fullname": new_random_user.fullname.lower(),
        "email": new_random_user.email,
        "role": "user",
    }.items() <= data.items()


async def test_register_user_with_existing_email(
    async_client: AsyncClient,
    registered_user: UserRegisterDTO,
):
    response = await async_client.post(base_url, json={**asdict(registered_user)})

    assert response.status_code == 409
    assert response.json()["detail"] == ERR_USER_EMAIL_ALREADY_EXISTS.format(
        email=registered_user.email
    )


async def test_register_user_with_invalid_email_format(
    async_client: AsyncClient, user_fullname: str
):
    response = await async_client.post(
        base_url,
        json={
            "email": "test@gmailcom",
            "password": "Test!@@@123",
            "fullname": user_fullname,
        },
    )
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["type"] == "value_error"
    assert data["detail"][0]["loc"][1] == "email"


async def test_register_user_with_weak_password(
    async_client: AsyncClient, user_fullname: str, faker_lib
):
    response = await async_client.post(
        base_url,
        json={
            "email": faker_lib.email(),
            "password": "Test1234",
            "fullname": user_fullname,
        },
    )
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["type"] == "value_error"
    assert data["detail"][0]["loc"][1] == "password"


async def test_register_user_with_missing_fields(
    async_client: AsyncClient, user_fullname, faker_lib
):
    response = await async_client.post(
        base_url,
        json={
            "email": faker_lib.email(),
            "fullname": user_fullname,
        },
    )
    data = response.json()

    assert response.status_code == 422
    assert data["detail"][0]["type"] == "missing"
    assert data["detail"][0]["loc"][1] == "password"
