import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.progress import WatchProgress
from app.models.movie import Movie
from app.schemas.progress import ProgressOut, ProgressUpdate

router = APIRouter()


@router.get("/{movie_id}", response_model=ProgressOut | None)
async def get_progress(movie_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WatchProgress).where(WatchProgress.movie_id == movie_id)
    )
    return result.scalar_one_or_none()


@router.post("/{movie_id}", response_model=ProgressOut)
async def save_progress(movie_id: str, body: ProgressUpdate, db: AsyncSession = Depends(get_db)):
    movie = await db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    result = await db.execute(
        select(WatchProgress).where(WatchProgress.movie_id == movie_id)
    )
    prog = result.scalar_one_or_none()

    now = datetime.utcnow()
    if prog:
        prog.position_seconds = body.position_seconds
        prog.completed = body.completed
        prog.last_watched_at = now
    else:
        prog = WatchProgress(
            id=str(uuid.uuid4()),
            movie_id=movie_id,
            position_seconds=body.position_seconds,
            completed=body.completed,
            last_watched_at=now,
        )
        db.add(prog)

    await db.commit()
    await db.refresh(prog)
    return prog
