import uuid
import shutil
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models.movie import Movie
from app.schemas.movie import MovieOut, TMDBSearchResult
from app.services.tmdb import tmdb_search, tmdb_get_details
from app.services.file_handler import get_video_duration
from app.config import settings

router = APIRouter()


@router.get("/tmdb/search", response_model=list[TMDBSearchResult])
async def search_tmdb(q: str = Query(..., min_length=1)):
    results = await tmdb_search(q)
    if results is None:
        raise HTTPException(status_code=503, detail="TMDB API unavailable — check TMDB_API_KEY")
    return results


@router.post("/tmdb/{tmdb_id}", response_model=MovieOut, status_code=201)
async def import_from_tmdb(tmdb_id: int, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Movie).where(Movie.tmdb_id == tmdb_id))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Movie already imported")

    details = await tmdb_get_details(tmdb_id)
    if not details:
        raise HTTPException(status_code=404, detail="TMDB movie not found")

    movie = Movie(
        id=str(uuid.uuid4()),
        title=details["title"],
        year=details.get("year"),
        genres=details.get("genres", []),
        overview=details.get("overview"),
        poster_url=details.get("poster_url"),
        tmdb_id=tmdb_id,
        runtime_minutes=details.get("runtime_minutes"),
        added_at=datetime.utcnow(),
    )
    db.add(movie)
    await db.commit()
    await db.refresh(movie)
    return movie


@router.post("/file/{movie_id}", response_model=MovieOut)
async def upload_video_file(
    movie_id: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    movie = await db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    allowed_types = {"video/mp4", "video/x-matroska", "video/webm", "video/quicktime"}
    if file.content_type and file.content_type not in allowed_types:
        ext = Path(file.filename or "").suffix.lower()
        if ext not in {".mp4", ".mkv", ".webm", ".mov", ".avi"}:
            raise HTTPException(status_code=400, detail="Unsupported video format")

    suffix = Path(file.filename or "video.mp4").suffix
    dest = settings.videos_path / f"{movie_id}{suffix}"

    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    movie.file_path = str(dest)

    duration = get_video_duration(str(dest))
    if duration and not movie.runtime_minutes:
        movie.runtime_minutes = duration // 60

    await db.commit()
    await db.refresh(movie)
    return movie


@router.post("/manual", response_model=MovieOut, status_code=201)
async def add_manual(
    title: str,
    year: int | None = None,
    youtube_embed_url: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    movie = Movie(
        id=str(uuid.uuid4()),
        title=title,
        year=year,
        youtube_embed_url=youtube_embed_url,
        added_at=datetime.utcnow(),
    )
    db.add(movie)
    await db.commit()
    await db.refresh(movie)
    return movie
