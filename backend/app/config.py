from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/moviestreamer"
    tmdb_api_key: str = ""
    videos_dir: str = "./videos"
    secret_key: str = "dev-secret-key"

    @property
    def videos_path(self) -> Path:
        p = Path(self.videos_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p


settings = Settings()
