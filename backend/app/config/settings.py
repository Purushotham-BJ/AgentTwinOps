"""Application settings loaded from environment variables.

Uses pydantic-settings to validate and coerce values at startup.
Every setting has a sensible default so the server can boot locally
without any .env file.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    """Immutable, validated application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ─────────────────────────────────────────────
    APP_NAME: str = "AgentTwinOps"
    APP_VERSION: str = "0.1.0"
    APP_DESCRIPTION: str = (
        "AI-powered Digital Twin & Multi-Agent DevOps platform"
    )
    APP_ENV: str = "development"
    APP_DEBUG: bool = False

    # ── Security ────────────────────────────────────────────────
    SECRET_KEY: SecretStr = Field(default=SecretStr("super-secret-default-key"))

    # ── Database ────────────────────────────────────────────────
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:admin_password@localhost:5432/agenttwinops"
    )

    # ── Server ──────────────────────────────────────────────────
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # ── CORS ────────────────────────────────────────────────────
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # ── Logging ─────────────────────────────────────────────────
    LOG_LEVEL: Literal[
        "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
    ] = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "console"

    # ── API ─────────────────────────────────────────────────────
    API_V1_PREFIX: str = "/api/v1"
    # ── Metrics collection interval ───────────────────────────────
    METRIC_STALE_THRESHOLD: int = 30  # seconds, default > collection interval

    # ── JWT / Auth ─────────────────────────────────────────────
    # Use existing SECRET_KEY for signing tokens; algorithm and expiry
    # can be configured via environment variables.
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # ── OAuth ──────────────────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:5173"
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: SecretStr = Field(default=SecretStr(""))
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/oauth/google/callback"
    GITHUB_CLIENT_ID: str = ""
    GITHUB_CLIENT_SECRET: SecretStr = Field(default=SecretStr(""))
    GITHUB_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/oauth/github/callback"
    OAUTH_STATE_TTL_SECONDS: int = 600

    # ── Paths ───────────────────────────────────────────────────
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    # ── Environment Validation ──────────────────────────────────
    @field_validator("APP_ENV", mode="before")
    def validate_app_env(cls, v: str) -> str:
        v = v.lower()
        if v not in ["development", "testing", "staging", "production"]:
            raise ValueError(f"Invalid environment: {v}")
        return v

    @property
    def is_development(self) -> bool:
        return self.APP_ENV == "development"

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    @property
    def is_testing(self) -> bool:
        return self.APP_ENV == "testing"


class DevelopmentConfig(BaseConfig):
    """Configuration for local development."""
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"
    LOG_FORMAT: Literal["json", "console"] = "console"


class TestingConfig(BaseConfig):
    """Configuration for automated tests."""
    APP_ENV: str = "testing"
    APP_DEBUG: bool = True
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "DEBUG"
    # Ensure tests run with a known secret key
    SECRET_KEY: SecretStr = Field(default=SecretStr("test-secret-key"))
    # Use same DB credentials as Docker compose for test DB
    DATABASE_URL: str = Field(default="postgresql+asyncpg://postgres:admin_password@localhost:5432/agenttwinops")


class ProductionConfig(BaseConfig):
    """Configuration for production environments."""
    APP_ENV: str = "production"
    APP_DEBUG: bool = False
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    LOG_FORMAT: Literal["json", "console"] = "json"

    @field_validator("SECRET_KEY", mode="after")
    def check_secret_key(cls, v: SecretStr) -> SecretStr:
        """Ensure a strong secret key is used in production."""
        if v.get_secret_value() in ["super-secret-default-key", "test-secret-key"]:
            raise ValueError("Default SECRET_KEY must not be used in production")
        return v


def get_config_class(env: str) -> type[BaseConfig]:
    """Return the appropriate config class for the environment."""
    envs = {
        "development": DevelopmentConfig,
        "testing": TestingConfig,
        "staging": ProductionConfig,
        "production": ProductionConfig,
    }
    return envs.get(env.lower(), DevelopmentConfig)


@lru_cache(maxsize=1)
def get_settings() -> BaseConfig:
    """Return a cached, singleton Settings instance (DI-friendly)."""
    # Create an initial instance just to read APP_ENV from the environment
    # Then instantiate the proper environment-specific class.
    env_state = BaseConfig().APP_ENV
    config_class = get_config_class(env_state)
    return config_class()


# Alias for backwards compatibility with existing imports
Settings = BaseConfig
