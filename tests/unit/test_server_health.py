# tests/test_server_health.py
import pytest
from fastapi import status
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_server_is_running():
    """Проверяем, что сервер работает и отвечает на запросы"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.json()
@pytest.mark.asyncio
async def test_api_docs_available():
    """Проверяем, что документация API доступна"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/docs")
        assert response.status_code == status.HTTP_200_OK
        assert "Swagger UI" in response.text