import httpx
import pytest

from app.config.settings import settings
from app.services.backend_client import BackendClient
import app.services.backend_client as backend_client_module


@pytest.mark.asyncio
async def test_stale_api_token_falls_back_to_service_login(monkeypatch):
    requests = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        if request.url.path == "/api/v1/incidents":
            if request.headers.get("authorization") == "Bearer stale-token":
                return httpx.Response(401, request=request)
            return httpx.Response(
                200,
                request=request,
                json={"success": True, "data": {"items": [{"id": "incident-1"}], "total": 1}},
            )
        if request.url.path == "/api/v1/auth/login":
            return httpx.Response(
                200,
                request=request,
                json={"success": True, "data": {"access_token": "fresh-token"}},
            )
        return httpx.Response(404, request=request)

    transport = httpx.MockTransport(handler)

    class MockAsyncClient(httpx.AsyncClient):
        def __init__(self, **kwargs):
            super().__init__(transport=transport, **kwargs)

    monkeypatch.setattr(backend_client_module.httpx, "AsyncClient", MockAsyncClient)
    monkeypatch.setattr(settings, "BACKEND_API_TOKEN", "stale-token")
    monkeypatch.setattr(settings, "BACKEND_SERVICE_EMAIL", "service@example.com")
    monkeypatch.setattr(settings, "BACKEND_SERVICE_PASSWORD", "StrongService@123")
    monkeypatch.setattr(settings, "AI_SERVICE_MODE", "real")

    client = BackendClient()
    incidents = await client.get_incidents()

    assert incidents == [{"id": "incident-1"}]
    assert [request.url.path for request in requests] == [
        "/api/v1/incidents",
        "/api/v1/auth/login",
        "/api/v1/incidents",
    ]
    assert requests[-1].headers["authorization"] == "Bearer fresh-token"


@pytest.mark.asyncio
async def test_missing_backend_credentials_raise_in_real_mode(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, request=request)

    transport = httpx.MockTransport(handler)

    class MockAsyncClient(httpx.AsyncClient):
        def __init__(self, **kwargs):
            super().__init__(transport=transport, **kwargs)

    monkeypatch.setattr(backend_client_module.httpx, "AsyncClient", MockAsyncClient)
    monkeypatch.setattr(settings, "BACKEND_API_TOKEN", "")
    monkeypatch.setattr(settings, "BACKEND_SERVICE_EMAIL", "")
    monkeypatch.setattr(settings, "BACKEND_SERVICE_PASSWORD", "")
    monkeypatch.setattr(settings, "AI_SERVICE_MODE", "real")

    with pytest.raises(Exception, match="Backend incidents API unavailable"):
        await BackendClient().get_incidents()


@pytest.mark.asyncio
async def test_invalid_service_credentials_raise_in_real_mode(monkeypatch):
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/v1/auth/login":
            return httpx.Response(401, request=request)
        return httpx.Response(401, request=request)

    transport = httpx.MockTransport(handler)

    class MockAsyncClient(httpx.AsyncClient):
        def __init__(self, **kwargs):
            super().__init__(transport=transport, **kwargs)

    monkeypatch.setattr(backend_client_module.httpx, "AsyncClient", MockAsyncClient)
    monkeypatch.setattr(settings, "BACKEND_API_TOKEN", "")
    monkeypatch.setattr(settings, "BACKEND_SERVICE_EMAIL", "service@example.com")
    monkeypatch.setattr(settings, "BACKEND_SERVICE_PASSWORD", "wrong-password")
    monkeypatch.setattr(settings, "AI_SERVICE_MODE", "real")

    with pytest.raises(Exception, match="Backend incidents API unavailable"):
        await BackendClient().get_incidents()
