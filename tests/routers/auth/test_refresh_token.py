from dataclasses import asdict
from datetime import timezone, datetime, timedelta

import pytest
import ulid
from faker.proxy import Faker
from httpx import AsyncClient
from jose import jwt
from sqlalchemy import insert, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.constants import auth_constants, token_constants
from app.auth.dtos import BlacklistedTokenDTO
from app.auth.enums import BlacklistReason, TokenType
from app.auth.models import BlacklistedToken
from app.users.models import User
from tests.conftest import login_user, get_user_by_email
from tests.dtos import UserRegisterDTO, AuthLoginOutDTO

base_url = f"/auth/refresh-token"

pytestmark = pytest.mark.anyio


async def get_token_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def test_refresh_token_success(
    async_client: AsyncClient, login_token: AuthLoginOutDTO
):
    async_client.cookies.set("refresh_token", login_token.refresh_token)
    response = await async_client.post(
        base_url,
        headers=await get_token_header(login_token.access_token),
    )
    data = response.json()

    assert response.status_code == 200
    assert data["access_token"] is not None, "Access Token is None"


async def test_refresh_token_missing_cookie(
    async_client: AsyncClient,
    registered_user: UserRegisterDTO,
):
    login_res = await async_client.post(
        "/auth/login",
        json={
            "email": registered_user.email,
            "password": registered_user.password,
        },
    )

    response = await async_client.post(
        base_url,
        headers={"Authorization": f"Bearer {login_res.json()['access_token']}"},
    )

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][1] == "refresh_token"


async def test_use_first_refresh_token_after_second_login_should_fail_if_revoked(
    async_client: AsyncClient,
    registered_user: UserRegisterDTO,
):
    login_res_1 = await async_client.post(
        "/auth/login",
        json={
            "email": registered_user.email,
            "password": registered_user.password,
        },
    )
    await async_client.post(
        "/auth/login",
        json={
            "email": registered_user.email,
            "password": registered_user.password,
        },
        headers={"Authorization": f"Bearer {login_res_1.json()['access_token']}"},
    )

    async_client.cookies.set("refresh_token", login_res_1.cookies.get("refresh_token"))
    response = await async_client.post(
        base_url,
        headers=await get_token_header(login_res_1.json()["access_token"]),
    )

    assert response.status_code == 401
    assert response.json()["detail"] == auth_constants.ERR_TOKEN_REVOKED.format(
        reason=BlacklistReason.TOKEN_ROTATION
    )


async def test_refresh_token_invalid_token(
    async_client: AsyncClient,
    login_token: AuthLoginOutDTO,
    faker_lib: Faker,
):
    async_client.cookies.set("refresh_token", faker_lib.text(max_nb_chars=120))
    response = await async_client.post(
        base_url, headers=await get_token_header(login_token.access_token)
    )
    data = response.json()

    print(data)
    assert response.status_code == 401
    assert data["detail"] == token_constants.JWT_CREDENTIALS_INVALID


async def test_refresh_token_expired_token(
    async_client: AsyncClient,
    db_session: AsyncSession,
    registered_user,
    settings,
):
    user = await get_user_by_email(registered_user.email, db_session)
    payload = {
        "sub": user.id,
        "jti": str(ulid.new()),
        "exp": datetime.now(timezone.utc) + timedelta(days=-1),
        "ip": "127.0.0.1",
        "iat": datetime.now(timezone.utc),
    }
    refresh_token = jwt.encode(
        payload, key=settings.SECRET_REFRESH_TOKEN, algorithm=settings.ALGORITHM
    )
    login_res = await login_user(async_client, UserRegisterDTO())

    async_client.cookies.set("refresh_token", refresh_token)
    response = await async_client.post(
        base_url, headers=await get_token_header(login_res.json())
    )

    assert response.status_code == 401
    assert response.json()["detail"] == token_constants.JWT_TOKEN_EXPIRED


async def test_refresh_token_blacklisted_token(
    async_client: AsyncClient,
    db_session: AsyncSession,
    login_token: AuthLoginOutDTO,
    settings,
):
    payload = jwt.decode(
        login_token.refresh_token,
        key=settings.SECRET_REFRESH_TOKEN,
        algorithms=[settings.ALGORITHM],
    )

    await db_session.execute(
        insert(BlacklistedToken).values(
            **asdict(
                BlacklistedTokenDTO(
                    jti=payload["jti"],
                    reason=BlacklistReason.COMPROMISED_TOKEN,
                    blacklisted_at=datetime.now(timezone.utc),
                )
            )
        )
    )
    await db_session.commit()

    async_client.cookies.set("refresh_token", login_token.refresh_token)
    response = await async_client.post(
        base_url, headers=await get_token_header(login_token.access_token)
    )

    assert response.status_code == 401
    assert response.json()["detail"] == auth_constants.ERR_TOKEN_REVOKED.format(
        reason=BlacklistReason.COMPROMISED_TOKEN
    )


async def test_refresh_token_wrong_token_type(
    async_client: AsyncClient, login_token: AuthLoginOutDTO
):
    async_client.cookies.set("refresh_token", login_token.access_token)
    response = await async_client.post(
        base_url, headers=await get_token_header(login_token.access_token)
    )

    assert response.status_code == 401
    assert (
        response.json()["detail"]
        == "Invalid token type: access_token'. Allowed types are: refresh_token."
    )


async def test_refresh_token_user_does_not_exist(
    async_client: AsyncClient,
    registered_user: UserRegisterDTO,
    db_session: AsyncSession,
):
    login_res = await async_client.post(
        "/auth/login",
        json={
            "email": registered_user.email,
            "password": registered_user.password,
        },
    )

    access_token = login_res.json()["access_token"]
    refresh_token = login_res.cookies.get("refresh_token")

    await db_session.execute(delete(User).where(User.email == registered_user.email))
    await db_session.commit()

    async_client.cookies.set("refresh_token", refresh_token)
    response = await async_client.post(
        base_url, headers=await get_token_header(access_token)
    )

    print(response.json())
    assert response.status_code == 401
    assert response.json()["detail"] == "User not found"


async def test_refresh_token_missing_claims(
    async_client: AsyncClient,
    registered_user: UserRegisterDTO,
    db_session: AsyncSession,
    settings,
):
    user = await get_user_by_email(registered_user.email, db_session)

    payload = {
        "sub": str(user.id),
        "exp": datetime.now(timezone.utc) + timedelta(days=1),
        "iat": datetime.now(timezone.utc),
        "type": TokenType.REFRESH_TOKEN,
        "jti": str(ulid.new()),
    }
    refresh_token = jwt.encode(
        payload, settings.SECRET_REFRESH_TOKEN, settings.ALGORITHM
    )

    login_res = await async_client.post(
        "/auth/login",
        json={
            "email": registered_user.email,
            "password": registered_user.password,
        },
    )

    async_client.cookies.set("refresh_token", refresh_token)
    response = await async_client.post(
        base_url, headers=await get_token_header(login_res.json()["access_token"])
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Token invalid."
