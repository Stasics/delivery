import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

@pytest.fixture(scope="session")
async def db_engine():
    engine = create_async_engine("postgresql+asyncpg://postgres:111@localhost:5432/quickparcel_test")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture
async def db_session(db_engine):
    async with db_engine.begin() as conn:
        AsyncSessionLocal = sessionmaker(conn, expire_on_commit=False, class_=AsyncSession)
        async with AsyncSessionLocal() as session:
            yield session
            await session.rollback()  # Откатываем транзакцию после теста