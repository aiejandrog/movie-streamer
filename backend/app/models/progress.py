import uuid
from datetime import datetime
from sqlalchemy import String, Integer, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class WatchProgress(Base):
    __tablename__ = "watch_progress"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    movie_id: Mapped[str] = mapped_column(String(36), ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, unique=True)
    position_seconds: Mapped[int] = mapped_column(Integer, default=0)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    last_watched_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
