from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.routers import movies, stream, watchlist, progress, ingest

app = FastAPI(title="MovieVault API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(movies.router, prefix="/api/movies", tags=["movies"])
app.include_router(stream.router, prefix="/api/stream", tags=["stream"])
app.include_router(watchlist.router, prefix="/api/watchlist", tags=["watchlist"])
app.include_router(progress.router, prefix="/api/progress", tags=["progress"])
app.include_router(ingest.router, prefix="/api/ingest", tags=["ingest"])


@app.get("/api/health")
async def health():
    return {"status": "ok"}


static_dir = Path(__file__).parent.parent / "static"
if static_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        return FileResponse(str(static_dir / "index.html"))
