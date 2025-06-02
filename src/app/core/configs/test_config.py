from pydantic_settings import SettingsConfigDict

from .base_config import BaseConfig


class TestConfig(BaseConfig):
    DATABASE_URL: str | None = None
    DATABASE_ECHO: bool | None = None

    SECRET_KEY: str | None = None
    SECRET_REFRESH_TOKEN: str | None = None
    SECRET_ACCESS_TOKEN: str | None = None
    SECURITY_PASSWORD_SALT: str | None = None
    ALGORITHM: str | None = None

    ACCESS_TOKEN_EXPIRE_MINUTES: int | None = None
    EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES: int | None = None
    REFRESH_TOKEN_EXPIRE_DAYS: int | None = None

    SMTP_HOST: str | None = None
    SMTP_PORT: int = 465
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None

    model_config = SettingsConfigDict(env_file=".env.test")
