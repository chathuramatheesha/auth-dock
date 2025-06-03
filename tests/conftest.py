import os
from dataclasses import asdict

import pytest
from faker.proxy import Faker
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .dtos import AuthLoginOutDTO, UserRegisterDTO

os.environ["APP_ENV"] = "test"

from app.core.configs.factory import get_config, ConfigTest
from app.db.database import async_engine, AsyncSessionLocal, Base
from app.db.dependencies import get_db
from app.main import app
from app.users.models import User

faker = Faker()
v1_url = "api/v1"


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app),
        base_url=f"http://test/{v1_url}",
    ) as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await async_engine.dispose()


async def override_get_db():
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
def override_dependency():
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session


@pytest.fixture
async def get_refresh_token_from_headers():
    async def _get_refresh_token(headers) -> str | None:
        set_cookie_headers = headers.get_list("set-cookie")
        refresh_token = None
        for cookie_str in set_cookie_headers:
            if cookie_str.startswith("refresh_token="):
                refresh_token = cookie_str
                break
        return refresh_token

    return _get_refresh_token


@pytest.fixture
async def faker_lib() -> Faker:
    return faker


@pytest.fixture
async def user_fullname() -> str:
    return f"{faker.first_name()} {faker.last_name()}"


@pytest.fixture
async def new_random_user(user_fullname: str) -> UserRegisterDTO:
    return UserRegisterDTO(
        fullname=user_fullname,
        password="Test1234!",
        email=faker.email(),
    )


async def register_user(async_client: AsyncClient, dto: UserRegisterDTO) -> dict:
    response = await async_client.post(
        f"/auth/signup",
        json={**asdict(dto)},
    )
    return response.json()


@pytest.fixture
async def registered_user(
    async_client: AsyncClient, user_fullname: str
) -> UserRegisterDTO:
    dto = UserRegisterDTO(
        fullname=user_fullname,
        email=faker.email(),
        password="Test1234!!22",
    )
    await register_user(async_client, dto)
    return dto


@pytest.fixture
async def test_user(
    async_client: AsyncClient,
    registered_user: UserRegisterDTO,
    db_session: AsyncSession,
) -> User:
    return await db_session.scalar(
        select(User).where(User.email == registered_user.email)
    )


@pytest.fixture
async def login_token(
    async_client: AsyncClient,
    registered_user: UserRegisterDTO,
    get_refresh_token_from_headers,
) -> AuthLoginOutDTO:
    response = await async_client.post(
        f"/auth/login",
        json={
            "email": registered_user.email,
            "password": registered_user.password,
        },
    )

    data = response.json()
    refresh_token = await get_refresh_token_from_headers(response.headers)

    return AuthLoginOutDTO(
        access_token=data["access_token"],
        token_type="bearer",
        refresh_token=refresh_token,
    )


@pytest.fixture
async def token_header(login_token: AuthLoginOutDTO) -> dict[str, str]:
    return {"Authorization": f"Bearer {login_token.access_token}"}


@pytest.fixture
async def settings() -> ConfigTest:
    return get_config()
