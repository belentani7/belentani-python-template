from __future__ import annotations
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.responses import JSONResponse

from {{cookiecutter.project_slug}}.interfaces.api.middleware.rate_limit import RateLimitMiddleware

@pytest.fixture
def app():
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware, requests_per_minute=5, requests_per_hour=100)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "ok"}
    
    @app.get("/health")
    async def health():
        return {"status": "ok"}
    
    return app

@pytest.fixture
def client(app):
    return TestClient(app)

class TestRateLimitMiddleware:
    def test_allows_requests_under_limit(self, client):
        for _ in range(5):
            response = client.get("/test")
            assert response.status_code == 200

    def test_blocks_requests_over_minute_limit(self, client):
        for _ in range(5):
            client.get("/test")
        response = client.get("/test")
        assert response.status_code == 429
        assert "Retry-After" in response.headers

    def test_excludes_health_endpoint(self, client):
        for _ in range(10):
            response = client.get("/health")
            assert response.status_code == 200

    def test_returns_retry_after_header(self, client):
        for _ in range(5):
            client.get("/test")
        response = client.get("/test")
        assert response.status_code == 429
        assert int(response.headers["Retry-After"]) > 0

    def test_different_clients_have_separate_limits(self, client):
        # This would require different client IPs - simplified test
        for _ in range(5):
            response = client.get("/test", headers={"X-Forwarded-For": "1.2.3.4"})
            assert response.status_code == 200
        response = client.get("/test", headers={"X-Forwarded-For": "1.2.3.4"})
        assert response.status_code == 429
        
        # Different IP should still work
        response = client.get("/test", headers={"X-Forwarded-For": "5.6.7.8"})
        assert response.status_code == 200;
