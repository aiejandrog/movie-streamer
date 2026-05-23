import httpx
from app.config import settings

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMG = "https://image.tmdb.org/t/p/w500"


async def tmdb_search(query: str) -> list[dict] | None:
    if not settings.tmdb_api_key:
        return None
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{TMDB_BASE}/search/movie",
            params={"api_key": settings.tmdb_api_key, "query": query, "language": "en-US"},
        )
    if resp.status_code != 200:
        return None
    results = resp.json().get("results", [])
    return [
        {
            "tmdb_id": r["id"],
            "title": r.get("title", ""),
            "year": int(r["release_date"][:4]) if r.get("release_date") else None,
            "overview": r.get("overview"),
            "poster_url": f"{TMDB_IMG}{r['poster_path']}" if r.get("poster_path") else None,
        }
        for r in results[:10]
    ]


async def tmdb_get_details(tmdb_id: int) -> dict | None:
    if not settings.tmdb_api_key:
        return None
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{TMDB_BASE}/movie/{tmdb_id}",
            params={"api_key": settings.tmdb_api_key, "language": "en-US"},
        )
    if resp.status_code != 200:
        return None
    d = resp.json()
    return {
        "title": d.get("title", ""),
        "year": int(d["release_date"][:4]) if d.get("release_date") else None,
        "genres": [g["name"] for g in d.get("genres", [])],
        "overview": d.get("overview"),
        "poster_url": f"{TMDB_IMG}{d['poster_path']}" if d.get("poster_path") else None,
        "runtime_minutes": d.get("runtime"),
    }
