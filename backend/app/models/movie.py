import uuid
import json
from datetime import datetime
from sqlalchemy import String, Integer, Text, DateTime, TypeDecorator
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class JSONList(TypeDecorator):
    """Stores a list as JSON text — works on both SQLite and PostgreSQL."""
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        return json.dumps(value) if value is not None else None

    def process_result_value(self, value, dialect):
        return json.loads(value) if value else []


class Movie(Base):
    __tablename__ = "movies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    genres: Mapped[list[str] | None] = mapped_column(JSONList, nullable=True)
    overview: Mapped[str | None] = mapped_column(Text, nullable=True)
    poster_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    tmdb_id: Mapped[int | None] = mapped_column(Integer, nullable=True, unique=True)
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    youtube_embed_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    runtime_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    added_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
