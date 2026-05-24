from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
import app.models  # noqa: F401 — registers all models with Base.metadata
from app.routers import movies, stream, watchlist, progress, ingest


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables if they don't exist yet.
    # Safe to call on every startup — skips existing tables.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


app = FastAPI(title="MovieVault API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

@app.middleware("http")
async def api_key_check(request: Request, call_next):
    """Optional API key protection. Only active when API_KEY is set in env."""
    if settings.api_key and request.url.path.startswith("/api/") and request.url.path != "/api/health":
        key = request.headers.get("X-API-Key")
        if key != settings.api_key:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
    return await call_next(request)


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
        if full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not found")
        if "." in Path(full_path).name:
            raise HTTPException(status_code=404, detail="Not found")
        return FileResponse(str(static_dir / "index.html"))
