# tests/integration/test_users.py
import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from main import app


@pytest.mark.asyncio
async def test_get_couriers_list():
    """Тестирование получения списка курьеров"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/users/api/auth/couriers")

        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.json(), list)
        # Можно добавить создание тестового курьера и проверку его наличия в списке