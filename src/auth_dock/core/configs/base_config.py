from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    APP_NAME: str | None = None
    APP_VERSION: str | None = None
    APP_LINK: str | None = None
    APP_ENV: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
