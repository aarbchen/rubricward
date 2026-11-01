"""
RubricWard API Gateway — Pydantic V2 Environment Configuration.
"""

import os
from pydantic import BaseModel, ConfigDict
try:
    from pydantic_settings import BaseSettings
except ImportError:
    BaseSettings = BaseModel  # type: ignore


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "RubricWard Commercial Payer MRF, Medicare RVU/GPCI, ERISA Appeal & NSA IDR API Gateway"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/v1"

    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5")

    RAPIDAPI_PROXY_SECRET: str = os.getenv(
        "RAPIDAPI_PROXY_SECRET",
        "rubricward-rapidapi-proxy-secret-2026",
    )
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_KEY", "")


settings = Settings()
