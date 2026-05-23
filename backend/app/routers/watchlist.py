import uuid
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.watchlist import WatchlistItem
from app.models.movie import Movie
from app.schemas.watchlist import WatchlistItemOut
from app.schemas.movie import MovieOut

router = APIRouter()


@router.get("", response_model=list[MovieOut])
async def get_watchlist(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Movie)
        .join(WatchlistItem, WatchlistItem.movie_id == Movie.id)
        .order_by(WatchlistItem.added_at.desc())
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/{movie_id}", status_code=201)
async def add_to_watchlist(movie_id: str, db: AsyncSession = Depends(get_db)):
    movie = await db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    existing = await db.execute(
        select(WatchlistItem).where(WatchlistItem.movie_id == movie_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already in watchlist")

    item = WatchlistItem(id=str(uuid.uuid4()), movie_id=movie_id, added_at=datetime.utcnow())
    db.add(item)
    await db.commit()
    return {"ok": True}


@router.delete("/{movie_id}", status_code=204)
async def remove_from_watchlist(movie_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WatchlistItem).where(WatchlistItem.movie_id == movie_id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Not in watchlist")
    await db.delete(item)
    await db.commit()
