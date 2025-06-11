import pytest
from app.models import User, Package, async_session
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.mark.asyncio
async def test_user_model():
    async with async_session() as db:
        user = User(
            email="test@example.com",
            hashed_password=pwd_context.hash("password"),
            phone="+1234567890",
            is_admin=False
        )
        db.add(user)
        await db.commit()
        assert user.id is not None
        assert user.verify_password("password") is True

@pytest.mark.asyncio
async def test_package_model():  # Use the fixture
    async with async_session() as db:
        package = Package(
            tracking_number="TRACK123",
            destination_pvz="PVZ1",
            status="created"
        )
        db.add(package)
        await db.commit()
        assert package.id is not None
        assert package.status == "created"