import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.constants import auth_constants
from app.users.models import User
from tests.conftest import get_refresh_token_from_headers
from tests.dtos import UserRegisterDTO
from tests.routers.auth import auth_base_url

pytestmark = pytest.mark.anyio
base_url = f"{auth_base_url}/login"


async def test_login_success(
    async_client: AsyncClient,
    registered_user: UserRegisterDTO,
    get_refresh_token_from_headers,
):
    response = await async_client.post(
        base_url,
        json={
            "email": registered_user.email,
            "password": registered_user.password,
        },
    )

    data: dict[str, str] = response.json()
    refresh_token = await get_refresh_token_from_headers(response.headers)

    assert refresh_token is not None, "Refresh token cookie not set"
    assert response.status_code == 200
    assert data["token_type"] == "bearer"
    assert "access_token" in data.keys()


async def test_login_wrong_password(
    async_client: AsyncClient, registered_user: UserRegisterDTO
):
    response = await async_client.post(
        base_url,
        json={
            "email": registered_user.email,
            "password": "TestPassword1!",
        },
    )
    data = response.json()

    assert response.status_code == 403
    assert data["detail"] == auth_constants.ERR_AUTH_INVALID_CREDENTIALS


async def test_login_with_unregistered_email(async_client: AsyncClient, faker_lib):
    response = await async_client.post(
        base_url,
        json={
            "email": faker_lib.email(),
            "password": "Test1234!!",
        },
    )
    data = response.json()

    assert response.status_code == 403
    assert data["detail"] == auth_constants.ERR_AUTH_INVALID_CREDENTIALS


async def test_login_with_missing_credentials(async_client: AsyncClient, faker_lib):
    response = await async_client.post(
        base_url,
        json={
            "email": faker_lib.email(),
            "password": faker_lib.password(),
        },
    )
    data = response.json()

    assert response.status_code == 403
    assert data["detail"] == auth_constants.ERR_AUTH_INVALID_CREDENTIALS


async def test_login_sets_refresh_token_cookie(
    async_client: AsyncClient,
    registered_user: UserRegisterDTO,
    get_refresh_token_from_headers,
):
    response = await async_client.post(
        base_url,
        json={
            "email": registered_user.email,
            "password": registered_user.password,
        },
    )
    refresh_token = await get_refresh_token_from_headers(response.headers)

    assert response.status_code == 200
    assert refresh_token is not None, "Refresh token cookie not set"


async def test_login_deactivated_user(
    async_client: AsyncClient,
    registered_user: UserRegisterDTO,
    db_session: AsyncSession,
):
    user: User = await db_session.scalar(
        select(User).where(User.email == registered_user.email)
    )
    user.is_active = False
    db_session.add(user)
    await db_session.commit()

    response = await async_client.post(
        base_url,
        json={
            "email": registered_user.email,
            "password": registered_user.password,
        },
    )
    data = response.json()

    assert response.status_code == 403
    assert data["detail"] == auth_constants.ERR_ACCOUNT_DEACTIVATED


async def test_login_deleted_user(
    async_client: AsyncClient,
    registered_user: UserRegisterDTO,
    db_session: AsyncSession,
):
    user: User = await db_session.scalar(
        select(User).where(User.email == registered_user.email)
    )
    user.is_deleted = True
    db_session.add(user)
    await db_session.commit()

    response = await async_client.post(
        base_url,
        json={
            "email": registered_user.email,
            "password": registered_user.password,
        },
    )
    data = response.json()

    assert response.status_code == 403
    assert data["detail"] == auth_constants.ERR_ACCOUNT_DELETED


# async def test_login_unverified_user()
