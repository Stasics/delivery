# tests/integration/test_auth.py
import pytest
import time
from fastapi import status
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_register_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Генерируем уникальные данные
        timestamp = str(int(time.time()))
        user_data = {
            "email": f"user{timestamp}@example.com",
            "password": "TestPass123!",
            "phone": f"+7910{timestamp[-6:]}",
            "full_name": "Test User"
        }

        # Регистрация
        response = await client.post(
            "/users/api/auth/register",
            json=user_data
        )

        assert response.status_code == status.HTTP_201_CREATED, \
            f"Ошибка регистрации: {response.json()}"


@pytest.mark.asyncio
async def test_login_user():
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Сначала регистрируем пользователя
        timestamp = str(int(time.time()))
        phone = f"+7910{timestamp[-6:]}"
        password = "TestPass123!"

        await client.post(
            "/users/api/auth/register",
            json={
                "email": f"login{timestamp}@test.com",
                "password": password,
                "phone": phone,
                "full_name": "Test User"
            }
        )

        # Логин (точно соответствует вашему LoginRequest)
        response = await client.post(
            "/users/api/auth/login",
            json={
                "phone": phone,
                "password": password
            }
        )

        assert response.status_code == status.HTTP_200_OK, \
            f"Ошибка входа: {response.json()}"
        assert "access_token" in response.json()