from __future__ import annotations

import logging

from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
import os

logger = logging.getLogger(__name__)

# Define environment state type
EnvironmentState = Literal["dev", "test", "prod"]

class BaseConfig(BaseSettings):
    """Base configuration with common settings"""
    ENV_STATE: EnvironmentState = "dev"  # Default to development

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

class GlobalConfig(BaseConfig):
    DATABASE_URL: str  # Required field
    DB_FORCE_ROLLBACK: bool = False

    # JWT Authentication settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    #AI settings


    @field_validator("DATABASE_URL")
    def validate_db_url(cls, v: str) -> str:
        if not v:
            raise ValueError("DATABASE_URL must be set")
        if "postgresql" in v and not os.getenv("POSTGRES_PASSWORD") and "@" not in v.split("//")[1]:
            raise ValueError("Invalid PostgreSQL URL format")
        return v

    @field_validator("SECRET_KEY")
    def validate_secret_key(cls, v: str) -> str:
        if not v:
            raise ValueError("SECRET_KEY must be set")
        return v

class DevConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="DEV_")

class TestConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="TEST_")
    DB_FORCE_ROLLBACK: bool = True

class ProdConfig(GlobalConfig):
    model_config = SettingsConfigDict(env_prefix="PROD_")

@lru_cache()
def get_config(env_state: EnvironmentState | None = None) -> GlobalConfig:
    env_state = env_state or BaseConfig().ENV_STATE or "dev"
    configs = {
        "dev": DevConfig,
        "test": TestConfig,
        "prod": ProdConfig
    }
    return configs[env_state]()

# Initialize config
config = get_config()
logger.debug("Current Environment: %s", config.ENV_STATE)
logger.debug("Database URL: %s", config.DATABASE_URL.split("@")[0] + "@[hidden]")