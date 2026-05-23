from datetime import datetime
from pydantic import BaseModel


class ProgressUpdate(BaseModel):
    position_seconds: int
    completed: bool = False


class ProgressOut(BaseModel):
    id: str
    movie_id: str
    position_seconds: int
    completed: bool
    last_watched_at: datetime

    model_config = {"from_attributes": True}
