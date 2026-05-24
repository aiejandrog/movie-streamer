"""
Basic API smoke tests.
Runs against SQLite in-memory — no external services needed.
TMDB tests expect 503 because TMDB_API_KEY is empty in CI.
"""
import io


async def test_health(client):
    r = await client.get("/api/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


async def test_movies_empty(client):
    r = await client.get("/api/movies")
    assert r.status_code == 200
    assert r.json() == []


async def test_movie_not_found(client):
    r = await client.get("/api/movies/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


async def test_watchlist_empty(client):
    r = await client.get("/api/watchlist")
    assert r.status_code == 200
    assert r.json() == []


async def test_tmdb_search_no_key(client):
    """Empty TMDB_API_KEY → 503, not 500."""
    r = await client.get("/api/ingest/tmdb/search?q=inception")
    assert r.status_code == 503


async def test_manual_add_and_retrieve(client):
    r = await client.post("/api/ingest/manual", params={"title": "Test Movie", "year": 2024})
    assert r.status_code == 201
    movie = r.json()
    assert movie["title"] == "Test Movie"
    assert movie["year"] == 2024

    r2 = await client.get(f"/api/movies/{movie['id']}")
    assert r2.status_code == 200
    assert r2.json()["title"] == "Test Movie"


async def test_watchlist_add_and_remove(client):
    r = await client.post("/api/ingest/manual", params={"title": "Watchlist Test"})
    movie_id = r.json()["id"]

    r = await client.post(f"/api/watchlist/{movie_id}")
    assert r.status_code == 201

    r = await client.get("/api/watchlist")
    assert any(m["id"] == movie_id for m in r.json())

    r = await client.delete(f"/api/watchlist/{movie_id}")
    assert r.status_code == 204

    r = await client.get("/api/watchlist")
    assert r.json() == []


async def test_watchlist_duplicate(client):
    r = await client.post("/api/ingest/manual", params={"title": "Dupe Test"})
    movie_id = r.json()["id"]

    await client.post(f"/api/watchlist/{movie_id}")
    r = await client.post(f"/api/watchlist/{movie_id}")
    assert r.status_code == 409


async def test_delete_movie(client):
    r = await client.post("/api/ingest/manual", params={"title": "Delete Me"})
    movie_id = r.json()["id"]

    r = await client.delete(f"/api/movies/{movie_id}")
    assert r.status_code == 204

    r = await client.get(f"/api/movies/{movie_id}")
    assert r.status_code == 404


# ── Security tests ───────────────────────────────────────────────────────────────

async def test_upload_path_traversal_blocked(client):
    """Non-UUID movie_id must be rejected before touching the filesystem."""
    r = await client.post(
        "/api/ingest/file/../../../etc/passwd",
        files={"file": ("test.mp4", io.BytesIO(b"fake"), "video/mp4")},
    )
    # FastAPI path normalisation may 404/405, our UUID check returns 400; all are safe
    assert r.status_code in (400, 404, 405, 422)


async def test_upload_invalid_extension_blocked(client):
    """Non-video extension must return 400."""
    r = await client.post("/api/ingest/manual", params={"title": "Ext Test"})
    movie_id = r.json()["id"]

    r = await client.post(
        f"/api/ingest/file/{movie_id}",
        files={"file": ("malware.exe", io.BytesIO(b"MZ"), "application/octet-stream")},
    )
    assert r.status_code == 400


async def test_progress_save_and_get(client):
    r = await client.post("/api/ingest/manual", params={"title": "Progress Test"})
    movie_id = r.json()["id"]

    r = await client.post(
        f"/api/progress/{movie_id}",
        json={"position_seconds": 120, "completed": False},
    )
    assert r.status_code == 200
    assert r.json()["position_seconds"] == 120

    r = await client.get(f"/api/progress/{movie_id}")
    assert r.status_code == 200
    assert r.json()["position_seconds"] == 120
