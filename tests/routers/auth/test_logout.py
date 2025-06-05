from datetime import timezone, datetime, timedelta

import pytest
import ulid
from httpx import AsyncClient
from jose import jwt
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.constants import auth_constants, token_constants
from app.auth.enums import BlacklistReason
from app.auth.models import BlacklistedToken
from tests.routers.auth import auth_base_url

pytestmark = pytest.mark.anyio
base_url = f"{auth_base_url}/logout"


async def test_logout_success(async_client: AsyncClient, token_header: dict):
    response = await async_client.post(
        base_url,
        headers=token_header,
    )

    assert response.status_code == 200
    assert response.json()["message"] == auth_constants.SUC_LOGOUT


async def test_logout_without_auth(async_client: AsyncClient):
    response = await async_client.post(
        base_url,
        headers={},
    )
    data = response.json()

    assert response.status_code == 403
    assert data["detail"] == "Not authenticated"


async def test_logout_invalid_token(async_client: AsyncClient):
    response = await async_client.post(
        base_url,
        headers={"Authorization": "Bearer test.fake.access_token"},
    )
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == token_constants.JWT_CREDENTIALS_INVALID


async def test_logout_blacklisted_token(
    async_client: AsyncClient,
    db_session: AsyncSession,
    login_token,
    settings,
):
    payload = jwt.decode(
        login_token.access_token,
        key=settings.SECRET_ACCESS_TOKEN,
        algorithms=[settings.ALGORITHM],
    )

    await db_session.execute(
        insert(BlacklistedToken).values(
            jti=payload["jti"],
            reason=BlacklistReason.LOGOUT,
            blacklisted_at=datetime.now(timezone.utc),
        ),
    )
    await db_session.commit()

    response = await async_client.post(
        base_url,
        headers={"Authorization": f"Bearer {login_token.access_token}"},
    )
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == auth_constants.ERR_TOKEN_REVOKED.format(
        reason=BlacklistReason.LOGOUT.value
    )


async def test_logout_expired_token(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user,
    settings,
):
    payload = {
        "sub": str(test_user.id),
        "jti": str(ulid.new()),
        "exp": datetime.now(timezone.utc) - timedelta(seconds=10),
        "iat": datetime.now(timezone.utc),
    }
    access_token = jwt.encode(
        payload,
        key=settings.SECRET_ACCESS_TOKEN,
        algorithm=settings.ALGORITHM,
    )

    response = await async_client.post(
        base_url,
        headers={"Authorization": f"Bearer {access_token}"},
    )
    data = response.json()

    assert response.status_code == 401
    assert data["detail"] == token_constants.JWT_TOKEN_EXPIRED.format(reaon="")


async def test_logout_multiple_times(async_client: AsyncClient, token_header):
    first_response = await async_client.post(
        f"{auth_base_url}/logout", headers=token_header
    )

    assert first_response.status_code == 200
    assert first_response.json()["message"] == auth_constants.SUC_LOGOUT

    second_response = await async_client.post(
        f"{auth_base_url}/logout", headers=token_header
    )

    assert second_response.status_code == 401
    assert second_response.json()["detail"] == auth_constants.ERR_TOKEN_REVOKED.format(
        reason=BlacklistReason.LOGOUT.value
    )


async def test_use_first_access_token_after_second_login_should_fail_if_revoked(
    async_client: AsyncClient,
    registered_user,
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

    response = await async_client.post(
        base_url,
        headers={"Authorization": f"Bearer {login_res_1.json()['access_token']}"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == auth_constants.ERR_TOKEN_REVOKED.format(
        reason=BlacklistReason.LOGIN.value
    )
