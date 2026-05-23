from datetime import datetime
from pydantic import BaseModel
from app.schemas.movie import MovieOut


class WatchlistItemOut(BaseModel):
    id: str
    movie_id: str
    added_at: datetime
    movie: MovieOut | None = None

    model_config = {"from_attributes": True}
