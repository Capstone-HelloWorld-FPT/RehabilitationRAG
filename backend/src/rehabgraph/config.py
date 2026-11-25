"""Settings from environment variables (BACKEND-ARCHITECTURE section 9).

Locally they come from backend/.env; on Railway from the service variables.
Only the settings the code uses today are declared; add the others with their first use.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    # JSON list, e.g. ["http://localhost:5173","https://rehabgraph.vercel.app"]
    cors_origins: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    return Settings()
