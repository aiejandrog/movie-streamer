import os
import aiofiles
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.movie import Movie

router = APIRouter()

CHUNK_SIZE = 1024 * 1024  # 1 MB chunks


@router.get("/{movie_id}")
async def stream_video(movie_id: str, request: Request, db: AsyncSession = Depends(get_db)):
    movie = await db.get(Movie, movie_id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    if not movie.file_path or not os.path.exists(movie.file_path):
        raise HTTPException(status_code=404, detail="Video file not found")

    file_size = os.path.getsize(movie.file_path)
    range_header = request.headers.get("Range")

    content_type = "video/mp4"
    if movie.file_path.lower().endswith(".mkv"):
        content_type = "video/x-matroska"
    elif movie.file_path.lower().endswith(".webm"):
        content_type = "video/webm"

    if range_header:
        range_val = range_header.replace("bytes=", "")
        parts = range_val.split("-")
        start = int(parts[0]) if parts[0] else 0
        end = int(parts[1]) if parts[1] else file_size - 1
        end = min(end, file_size - 1)
        length = end - start + 1

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

        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(length),
            "Content-Type": content_type,
        }
        return StreamingResponse(ranged_stream(), status_code=206, headers=headers)

    async def full_stream():
        async with aiofiles.open(movie.file_path, "rb") as f:
            while True:
                chunk = await f.read(CHUNK_SIZE)
                if not chunk:
                    break
                yield chunk

    headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(file_size),
        "Content-Type": content_type,
    }
    return StreamingResponse(full_stream(), status_code=200, headers=headers)
