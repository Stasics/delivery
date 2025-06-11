import pytest
from fastapi import status
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_home_route():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"message": "Hello, World! from FastAPI on Render"}

@pytest.mark.asyncio
async def test_login_route():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/users/api/auth/login",
            json={"phone": "+1234567890", "password": "password"}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST  # Пользователь не существует