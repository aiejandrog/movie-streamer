import asyncio
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.movie import Movie

router = APIRouter()

CHUNK_SIZE = 1024 * 1024        # 1 MB read chunks
MAX_RANGE_BYTES = 100 * 1024 * 1024  # 100 MB max per range request


def _content_type(path: str) -> str:
    p = path.lower()
    if p.endswith(".mkv"):
        return "video/x-matroska"
    if p.endswith(".webm"):
        return "video/webm"
    return "video/mp4"


@router.get("/{movie_id}")
async def stream_video(movie_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    movie = await db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    if not movie.file_path:
        raise HTTPException(status_code=404, detail="No video file attached")

    # Async stat to avoid blocking the event loop
    try:
        stat = await asyncio.to_thread(lambda: __import__("os").stat(movie.file_path))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Video file not found on disk")

    file_size = stat.st_size
    content_type = _content_type(movie.file_path)
    range_header = request.headers.get("Range")

    if range_header:
        try:
            range_val = range_header.strip().removeprefix("bytes=")
            parts = range_val.split("-")
            start = int(parts[0]) if parts[0] else 0
            end = int(parts[1]) if len(parts) > 1 and parts[1] else file_size - 1
        except (ValueError, IndexError):
            raise HTTPException(status_code=416, detail="Invalid Range header")

        if start < 0 or start >= file_size or end < start:
            raise HTTPException(status_code=416, detail="Range not satisfiable")

        end = min(end, file_size - 1)
        length = end - start + 1

        # Cap range size to avoid memory exhaustion
        if length > MAX_RANGE_BYTES:
            end = start + MAX_RANGE_BYTES - 1
            length = MAX_RANGE_BYTES

        async def ranged_stream():
            async with aiofiles.open(movie.file_path, "rb") as f:
                await f.seek(start)
                remaining = length
                while remaining > 0:
                    chunk = await f.read(min(CHUNK_SIZE, remaining))
                    if not chunk:
                        break
                    remaining -= len(chunk)
                    yield chunk

        return StreamingResponse(ranged_stream(), status_code=206, headers={
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(length),
            "Content-Type": content_type,
        })

    async def full_stream():
        async with aiofiles.open(movie.file_path, "rb") as f:
            while True:
                chunk = await f.read(CHUNK_SIZE)
                if not chunk:
                    break
                yield chunk

    return StreamingResponse(full_stream(), status_code=200, headers={
        "Accept-Ranges": "bytes",
        "Content-Length": str(file_size),
        "Content-Type": content_type,
    })
