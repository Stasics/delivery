# tests/integration/test_packages.py
import pytest
import time
from fastapi import status
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_create_and_get_package():
    """Тестирование создания и получения информации о посылке"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # 1. Регистрация и логин пользователя
        timestamp = str(int(time.time()))
        user_data = {
            "email": f"package_user_{timestamp}@example.com",
            "password": "PackagePass123!",
            "phone": f"+7910{timestamp[-6:]}",
            "full_name": "Package Test User"
        }

        # Регистрация
        await client.post("/users/api/auth/register", json=user_data)

        # Логин
        login_res = await client.post(
            "/users/api/auth/login",
            json={"phone": user_data["phone"], "password": user_data["password"]}
        )
        token = login_res.json()["access_token"]

        # 2. Создание посылки
        package_data = {
            "tracking_number": f"PKG{timestamp[-6:]}",
            "destination_pvz": "Test PVZ",
            "user_id": 1,  # ID обычно присваивается автоматически
            "weight": 1.5,
            "price": 100.0
        }

        create_res = await client.post(
            "/users/api/auth/packages/",
            json=package_data,
            headers={"Authorization": f"Bearer {token}"}
        )

        assert create_res.status_code == status.HTTP_201_CREATED
        assert create_res.json()["tracking_number"] == package_data["tracking_number"]

        # 3. Получение информации о посылке
        get_res = await client.get(
            f"/users/api/auth/packages/{package_data['tracking_number']}",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert get_res.status_code == status.HTTP_200_OK
        assert get_res.json()["destination_pvz"] == package_data["destination_pvz"]
        assert get_res.json()["status"] == "created"