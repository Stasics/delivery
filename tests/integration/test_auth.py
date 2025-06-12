# tests/integration/test_stub_auth.py
from fastapi import APIRouter
from fastapi.testclient import TestClient

# Создаем роутер-заглушку
stub_router = APIRouter()


@stub_router.post("/users/api/auth/login")
def stub_login():
    return {"access_token": "stub-token", "token_type": "bearer"}


def test_stub_login():
    client = TestClient(stub_router)
    response = client.post("/users/api/auth/login", json={})  # Данные не проверяются

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "stub-token",
        "token_type": "bearer"
    }