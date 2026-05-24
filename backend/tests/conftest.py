import pytest
from httpx import AsyncClient, ASGITransport
from app.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
async def clean_db():
    """Create all tables before each test, drop after — guaranteed clean state."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(clean_db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
