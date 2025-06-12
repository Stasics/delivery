# tests/integration/conftest.py
import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

from app.models import Base, User
from main import app
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db_engine():
    engine = create_async_engine("postgresql+asyncpg://postgres:111@postgres:5432/quickparcel")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def db(db_engine):
    async with db_engine.connect() as connection:
        async_session = sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False
        )
        async with async_session() as session:
            try:
                yield session
            finally:
                await session.rollback()

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def test_user(db):
    hashed_password = pwd_context.hash("testpassword")
    user = User(
        email="test@example.com",
        hashed_password=hashed_password,
        phone="+1234567890",
        full_name="Test User"
    )
    db.add(user)
    await db.commit()
    return user

@pytest.fixture
async def auth_token(client, test_user):
    login_data = {
        "phone": "+1234567890",
        "password": "testpassword"
    }
    response = await client.post("/users/api/auth/login", data=login_data)
    return response.json()["access_token"]

@pytest.fixture
async def auth_client(client, auth_token):
    client.headers.update({"Authorization": f"Bearer {auth_token}"})
    return client

