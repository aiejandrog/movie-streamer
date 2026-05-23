from datetime import datetime
from pydantic import BaseModel


class MovieBase(BaseModel):
    title: str
    year: int | None = None
    genres: list[str] | None = None
    overview: str | None = None
    poster_url: str | None = None
    tmdb_id: int | None = None
    file_path: str | None = None
    youtube_embed_url: str | None = None
    runtime_minutes: int | None = None


class MovieCreate(MovieBase):
    pass


class MovieOut(MovieBase):
    id: str
    added_at: datetime

    model_config = {"from_attributes": True}


class TMDBSearchResult(BaseModel):
    tmdb_id: int
    title: str
    year: int | None
    overview: str | None
    poster_url: str | None
