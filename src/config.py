from pydantic_settings import BaseSettings
from typing import Optional
import secrets


def _default_secret_key() -> str:
    """Generate a random secret key if none is provided via environment."""
    return secrets.token_hex(32)


class Settings(BaseSettings):
    # API
    API_TITLE: str = "AI Universe"
    API_VERSION: str = "1.0.0"

    # Database
    DATABASE_URL: str = "sqlite:///./ai_universe.db"

    # Redis (optional – used for joke caching when available)
    REDIS_URL: Optional[str] = None

    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Security – set SECRET_KEY in your environment for production
    SECRET_KEY: str = _default_secret_key()
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Server
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS – restrict in production via CORS_ORIGINS env variable
    # e.g. CORS_ORIGINS='["https://myapp.example.com"]'
    # Defaults to localhost origins for development safety.
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]

    # Joke cache TTL in seconds
    JOKE_CACHE_TTL: int = 300

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
