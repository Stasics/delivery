from app.routers.user_routes import create_access_token
from datetime import timedelta

def test_token_creation():
    token = create_access_token({"sub": "test@example.com"}, timedelta(minutes=15))
    assert isinstance(token, str)
    assert len(token) > 0