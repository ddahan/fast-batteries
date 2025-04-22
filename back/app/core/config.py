from datetime import timedelta
from functools import lru_cache
from pathlib import Path
from typing import Annotated, Literal, Self
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

from fastapi import Depends
from pydantic import PostgresDsn, RedisDsn, computed_field, model_validator
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ######################################################################################
    # Main
    ######################################################################################

    BASE_DIR: Path = Path(__file__).resolve().parents[2]
    APP_TITLE: str = "🔋 Fast Batteries"
    APP_VERSION: str = "0.1.0"
    DOCS_URL: str = "/"
    REDIRECT_SLASHES: bool = False  # errors with slashes are more explicit this way
    ENVIRONMENT: str
    TIMEZONE: ZoneInfo = ZoneInfo("Europe/Paris")
    PHONE_REGION_CODE: str = "FR"
    DEFAULT_ITEMS_PER_PAGE: int = 10
    MAX_ITEMS_PER_PAGE: int = 50
    FRONT_DOMAIN: str
    BACK_DOMAIN: str

    @computed_field
    @property
    def FRONT_URL(self) -> str:
        return f"{self.PROTOCOL}://{self.FRONT_DOMAIN}"

    @computed_field
    @property
    def BACK_URL(self) -> str:
        return f"{self.PROTOCOL}://{self.BACK_DOMAIN}"

    @computed_field
    @property
    def MAIN_LOGO_URL(self) -> str:
        # would not work with FRONT_URL as an email can't display an image from localhost
        return "https://fast-batteries.ovh/favicon/battery.png"

    ######################################################################################
    # Logging
    ######################################################################################

    USE_LOGFIRE: bool
    LOGFIRE_TOKEN: str | None = None

    @model_validator(mode="after")
    def check_logfire_token(self) -> Self:
        if self.USE_LOGFIRE is True and self.LOGFIRE_TOKEN is None:
            raise ValueError("LOGFIRE_TOKEN is required when USE_LOGFIRE is True.")
        return self

    ######################################################################################
    # Security
    ######################################################################################

    DEBUG: bool
    PROTOCOL: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE: timedelta = timedelta(days=7)
    EMAIL_RESET_TOKEN_EXPIRE: timedelta = timedelta(minutes=30)
    ALGORITHM: str = "HS256"
    CORS_ALLOW_ORIGIN: list[str]
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True

    ######################################################################################
    # Social Auth
    ######################################################################################

    LINKEDIN_CLIENT_ID: str
    LINKEDIN_CLIENT_SECRET: str
    LINKEDIN_AUTHORIZATION_URL: str = "https://www.linkedin.com/oauth/v2/authorization"
    LINKEDIN_TOKEN_URL: str = "https://www.linkedin.com/oauth/v2/accessToken"
    LINKEDIN_PROFILE_URL: str = "https://api.linkedin.com/v2/userinfo"
    LINKEDIN_SCOPES: str = "openid email profile"

    @computed_field
    @property
    def LINKEDIN_REDIRECT_URI(self) -> str:
        return urljoin(self.BACK_URL, "auth/linkedin/callback")

    @computed_field
    @property
    def SOCIAL_AUTH_FRONT_REDIRECT_URL(self) -> str:
        return urljoin(self.FRONT_URL, "auth/social-result")

    ######################################################################################
    # Email
    ######################################################################################

    EMAIL_BACKEND: Literal[
        "smtp",  # send a real email
        "console",  # display email in the console
        "dummy",  # does nothing except a simple log
    ]
    EMAIL_FROM_NAME: str = "Fast Batteries Team"
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    SMTP_PORT: int = 587
    SMTP_USE_TLS: bool = True

    @model_validator(mode="after")
    def check_smtp_fields(self) -> Self:
        required_if_smtp = ["SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD"]

        if self.EMAIL_BACKEND == "smtp":
            for field_name in required_if_smtp:
                if getattr(self, field_name) is None:
                    raise ValueError(
                        f'{field_name} is required when EMAIL_BACKEND is set to "smtp"'
                    )
        return self

    @computed_field
    @property
    def EMAIL_FROM_EMAIL(self) -> str:
        return "contact@fast-batteries.ovh"  # would not work with contact@localhost:3000

    @computed_field
    @property
    def EMAIL_TEMPLATES_BUILD_PATH(self) -> Path:
        return self.BASE_DIR / "app" / "email_templates" / "build"

    ######################################################################################
    # Database & PostgreSQL
    ######################################################################################

    DATABASE_ALLOW_RESET: bool  # prevent human error in production env
    DATABASE_ECHO: bool

    @computed_field
    @property
    def ALEMBIC_CONFIG_PATH(self) -> Path:
        return self.BASE_DIR / "alembic.ini"

    @computed_field
    @property
    def ALEMBIC_MIGRATION_PATH(self) -> Path:
        return self.BASE_DIR / "migrations"

    @computed_field
    @property
    def ALEMBIC_MIGRATION_VERSION_PATH(self) -> Path:
        return self.ALEMBIC_MIGRATION_PATH / "versions"

    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    @computed_field
    @property
    def POSTGRES_URI(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+psycopg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                path=self.POSTGRES_DB,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
            )
        )

    # NOTE: these fields are necessary as POSTGRES_USER and POSTGRES_PASSWORD will
    # be overrided with test values when running pytest. We need an admin connection
    # during tests.
    POSTGRES_ADMIN_USER: str
    POSTGRES_ADMIN_PASSWORD: str

    @computed_field
    @property
    def POSTGRES_ADMIN_URI(self) -> str:
        return str(
            PostgresDsn.build(
                scheme="postgresql+psycopg",
                username=self.POSTGRES_ADMIN_USER,
                password=self.POSTGRES_ADMIN_PASSWORD,
                path="postgres",
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
            )
        )

    ######################################################################################
    # Redis
    ######################################################################################

    REDIS_SERVER: str
    REDIS_DB: int = 0
    REDIS_PORT: int = 6379

    @computed_field
    @property
    def REDIS_URI(self) -> str:
        return str(
            RedisDsn.build(
                scheme="redis",
                path=str(self.REDIS_DB),
                host=self.REDIS_SERVER,
                port=self.REDIS_PORT,
            )
        )

    ######################################################################################
    # Celery
    ######################################################################################

    celery_timezone: ZoneInfo = TIMEZONE

    @computed_field
    @property
    def celery_broker_url(self) -> str:
        return self.REDIS_URI

    @computed_field
    @property
    def celery_result_backend(self) -> str:
        return str(
            MultiHostUrl.build(
                scheme="db+postgresql+psycopg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                path=self.POSTGRES_DB,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
            )
        )

    # https://docs.celeryq.dev/en/stable/userguide/configuration.html#result-extended
    celery_result_extended: bool = True

    # https://docs.celeryq.dev/en/stable/userguide/configuration.html#broker-connection-retry-on-startup
    celery_broker_connection_retry_on_startup: bool = False  # removes warning

    # https://docs.celeryq.dev/en/stable/userguide/configuration.html#beat-scheduler
    celery_beat_scheduler: str = "app.core.scheduling:MyDatabaseScheduler"

    ######################################################################################
    # MinIO
    ######################################################################################

    MINIO_SERVER: str
    MINIO_PORT: int
    MINIO_ACCESS_KEY: str
    MINIO_SECRET_KEY: str
    MINIO_BUCKET_NAME: str

    @computed_field
    @property
    def MINIO_ENDPOINT(self) -> str:
        return f"http://{self.MINIO_SERVER}:{self.MINIO_PORT}"

    ######################################################################################
    # Model Config (used for Pydantic configuration)
    # https://docs.pydantic.dev/latest/concepts/pydantic_settings
    ######################################################################################

    model_config = SettingsConfigDict(
        # only for local .env files. Would be overrided by existing env vars
        env_file=BASE_DIR / ".env",
        env_ignore_empty=True,
        env_prefix="FAPI_",
        case_sensitive=True,
        extra="forbid",
    )


@lru_cache
def get_settings() -> Settings:
    """Injectable dependency"""
    # https://fastapi.tiangolo.com/advanced/settings/#creating-the-settings-only-once-with-lru_cache
    return Settings()  # type: ignore


SettingsDep = Annotated[Settings, Depends(get_settings)]
