from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.database import get_db
from app.models.movie import Movie
from app.schemas.movie import MovieOut

router = APIRouter()


@router.get("", response_model=list[MovieOut])
async def list_movies(
    q: str | None = Query(None),
    genre: str | None = Query(None),
    year: int | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Movie).order_by(Movie.added_at.desc())

    if q:
        stmt = stmt.where(Movie.title.ilike(f"%{q}%"))
    if year:
        stmt = stmt.where(Movie.year == year)
    if genre:
        stmt = stmt.where(Movie.genres.like(f'\'%"{genre}"%\''))

    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/continuing", response_model=list[MovieOut])
async def continue_watching(db: AsyncSession = Depends(get_db)):
    from app.models.progress import WatchProgress
    stmt = (
        select(Movie)
        .join(WatchProgress, WatchProgress.movie_id == Movie.id)
        .where(WatchProgress.completed == False, WatchProgress.position_seconds > 0)
        .order_by(WatchProgress.last_watched_at.desc())
        .limit(10)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{movie_id}", response_model=MovieOut)
async def get_movie(movie_id: str, db: AsyncSession = Depends(get_db)):
    movie = await db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.delete("/{movie_id}", status_code=204)
async def delete_movie(movie_id: str, db: AsyncSession = Depends(get_db)):
    movie = await db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    await db.delete(movie)
    await db.commit()
