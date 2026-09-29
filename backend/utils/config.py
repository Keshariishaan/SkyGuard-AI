"""
Central place that reads environment variables (.env). Nothing else in
the backend should call os.environ directly - import `settings` instead.
"""

import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_SECRET_KEY: str = os.getenv("APP_SECRET_KEY", "change-me-in-production")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./skyguard.db")

    CORS_ORIGINS: list = [
        o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()
    ]

    DEFAULT_SEED: int = int(os.getenv("DEFAULT_SEED", "42"))
    DEFAULT_CONTAMINATION: float = float(os.getenv("DEFAULT_CONTAMINATION", "0.08"))

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))


settings = Settings()
