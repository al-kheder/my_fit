from __future__ import annotations

from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
import os

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
    """Global configuration shared across all environments"""
    DATABASE_URL: str  # Required field
    DB_FORCE_ROLLBACK: bool = False

    @field_validator("DATABASE_URL")
    def validate_db_url(cls, v: str) -> str:
        """Validate the database URL"""
        if not v:
            raise ValueError("DATABASE_URL must be set")
        if "postgresql" in v and not os.getenv("POSTGRES_PASSWORD") and "@" not in v.split("//")[1]:
            raise ValueError("Invalid PostgreSQL URL format")
        return v

class DevConfig(GlobalConfig):
    """Development specific configuration"""
    model_config = SettingsConfigDict(env_prefix="DEV_")

class TestConfig(GlobalConfig):
    """Testing specific configuration"""
    model_config = SettingsConfigDict(env_prefix="TEST_")
    DB_FORCE_ROLLBACK: bool = True

class ProdConfig(GlobalConfig):
    """Production specific configuration"""
    model_config = SettingsConfigDict(env_prefix="PROD_")

@lru_cache()
def get_config(env_state: EnvironmentState | None = None) -> GlobalConfig:
    """Get the appropriate config based on environment state"""
    env_state = env_state or BaseConfig().ENV_STATE or "dev"

    configs = {
        "dev": DevConfig,
        "test": TestConfig,
        "prod": ProdConfig
    }

    return configs[env_state]()

# Initialize config
config = get_config()
print(f"Config loaded for {config.ENV_STATE} environment")
print(f"Database URL: {config.DATABASE_URL.split('@')[0]}@[hidden]")