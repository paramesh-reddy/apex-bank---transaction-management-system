import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "Apex Bank Account & Transaction Management System"
    API_V1_STR: str = "/api/v1"
    APP_ENV: str = "development"

    # Database
    DATABASE_URL: str = (
        "postgresql+psycopg://neondb_owner:npg_cB1oTNHC6Fga@ep-sweet-wildflower-b5tiqheb-pooler.c-7.us-east-2.aws.neon.tech/neondb?sslmode=require"
    )

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "*",
    ]

    @field_validator("DATABASE_URL", mode="before")
    def fix_database_url(cls, v: str) -> str:
        if not v:
            return v
        # Ensure psycopg 3 driver is used with SQLAlchemy 2
        if v.startswith("postgresql://") and not v.startswith("postgresql+psycopg://"):
            v = v.replace("postgresql://", "postgresql+psycopg://", 1)
        elif v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+psycopg://", 1)
        # channel_binding parameter is specific to libpq connection args, not all poolers
        if "channel_binding=require" in v:
            v = v.replace("&channel_binding=require", "").replace("channel_binding=require&", "").replace("channel_binding=require", "")
            if v.endswith("?"):
                v = v[:-1]
        return v

    @field_validator("CORS_ORIGINS", mode="before")
    def parse_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
