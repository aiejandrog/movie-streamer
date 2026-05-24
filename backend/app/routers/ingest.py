import uuid
import aiofiles
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

ALLOWED_SUFFIXES = {".mp4", ".mkv", ".webm", ".mov", ".avi"}
MAX_UPLOAD_BYTES = 50 * 1024 * 1024 * 1024  # 50 GB


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
    # Validate movie_id is a proper UUID — prevents path traversal
    try:
        safe_id = str(uuid.UUID(movie_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid movie ID")

    movie = await db.get(Movie, safe_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    # Validate extension from filename (don't trust content_type — easily spoofed)
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=400, detail=f"Unsupported format. Allowed: {', '.join(ALLOWED_SUFFIXES)}")

    dest = settings.videos_path / f"{safe_id}{suffix}"

    # Async chunked write with size cap
    bytes_written = 0
    async with aiofiles.open(dest, "wb") as out:
        while True:
            chunk = await file.read(1024 * 1024)  # 1 MB at a time
            if not chunk:
                break
            bytes_written += len(chunk)
            if bytes_written > MAX_UPLOAD_BYTES:
                await out.close()
                dest.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="File too large (50 GB max)")
            await out.write(chunk)

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
