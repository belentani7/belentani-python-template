from __future__ import annotations
import pytest
from datetime import datetime, timedelta
from jose import jwt
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

from {{cookiecutter.project_slug}}.config.settings import get_settings
from {{cookiecutter.project_slug}}.interfaces.api.middleware.auth import (
    get_current_user,
    create_access_token,
    CurrentUser,
)

settings = get_settings()

@pytest.fixture
def app():
    app = FastAPI()
    
    @app.get("/protected")
    async def protected_endpoint(user: CurrentUser = Depends(get_current_user)):
        return {"user_id": user.id, "email": user.email}
    
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

def create_test_token(user_id: str = "test-user", scopes: list = None, expired: bool = False) -> str:
    data = {"sub": user_id, "scopes": scopes or []}
    if expired:
        data["exp"] = datetime.utcnow() - timedelta(hours=1)
    else:
        data["exp"] = datetime.utcnow() + timedelta(hours=1)
    data["iat"] = datetime.utcnow()
    return jwt.encode(data, settings.secret_key, algorithm=settings.algorithm)

class TestAuthMiddleware:
    def test_rejects_missing_token(self, client):
        response = client.get("/protected")
        assert response.status_code == 401
        assert response.json()["detail"] == "Not authenticated"

    def test_rejects_invalid_token(self, client):
        response = client.get("/protected", headers={"Authorization": "Bearer invalid-token"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token"

    def test_rejects_expired_token(self, client):
        token = create_test_token(expired=True)
        response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token"

    def test_accepts_valid_token(self, client):
        token = create_test_token("test-user-123")
        response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == "test-user-123"

    def test_token_with_scopes(self, client):
        token = create_test_token("test-user", scopes=["read", "write"])
        response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

    def test_create_access_token(self):
        token = create_access_token({"sub": "test", "scopes": ["read"]})
        decoded = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        assert decoded["sub"] == "test"
        assert decoded["scopes"] == ["read"]
        assert "exp" in decoded
        assert "iat" in decoded;
