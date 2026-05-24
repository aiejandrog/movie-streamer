from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/moviestreamer"
    tmdb_api_key: str = ""
    videos_dir: str = "./videos"
    secret_key: str = "dev-secret-key"
    # Comma-separated allowed origins. Set in .env for production.
    # Default allows local dev; Railway will set this to the actual domain.
    allowed_origins: str = "http://localhost:5173,http://localhost:4173"
    # Optional API key protection. Leave empty for local dev (no auth).
    # Set in Railway dashboard to instantly lock down the API.
    api_key: str = ""

    @property
    def async_database_url(self) -> str:
        """Normalise the DB URL to the asyncpg driver.

        Railway's PostgreSQL plugin provides a plain ``postgresql://`` (or
        ``postgres://``) URL.  SQLAlchemy's async engine requires the
        ``+asyncpg`` dialect.  This property handles the conversion so the raw
        DATABASE_URL env var can be set as-is from the Railway dashboard.
        """
        url = self.database_url
        if url.startswith("postgres://"):
            url = "postgresql+asyncpg://" + url[len("postgres://"):]
        elif url.startswith("postgresql://") and "+asyncpg" not in url:
            url = "postgresql+asyncpg://" + url[len("postgresql://"):]
        return url

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def videos_path(self) -> Path:
        p = Path(self.videos_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
