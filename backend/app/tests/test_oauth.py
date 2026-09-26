import pytest
from fastapi import HTTPException
from pydantic import SecretStr

from app.services.oauth import OAuthService


def test_oauth_state_round_trip():
    service = OAuthService(None)
    state = service._encode_state("google", None)
    payload = service._decode_state(state, "google")
    assert payload["provider"] == "google"


def test_oauth_state_rejects_provider_mismatch():
    service = OAuthService(None)
    state = service._encode_state("google", None)
    with pytest.raises(HTTPException) as error:
        service._decode_state(state, "github")
    assert error.value.status_code == 400


def test_oauth_state_rejects_expired(monkeypatch):
    service = OAuthService(None)
    monkeypatch.setattr("app.services.oauth.settings.OAUTH_STATE_TTL_SECONDS", -1)
    state = service._encode_state("google", None)
    with pytest.raises(HTTPException):
        service._decode_state(state, "google")


def test_authorization_url_contains_configured_redirect(monkeypatch):
    service = OAuthService(None)
    monkeypatch.setattr("app.services.oauth.settings.GOOGLE_CLIENT_ID", "google-client")
    monkeypatch.setattr("app.services.oauth.settings.GOOGLE_CLIENT_SECRET", SecretStr("google-secret"))
    url = service.authorization_url("google")
    assert "client_id=google-client" in url
    assert "redirect_uri=http%3A%2F%2Flocalhost%3A8000%2Fapi%2Fv1%2Fauth%2Foauth%2Fgoogle%2Fcallback" in url


def test_authorization_url_requires_client_secret(monkeypatch):
    service = OAuthService(None)
    monkeypatch.setattr("app.services.oauth.settings.GOOGLE_CLIENT_ID", "google-client")
    monkeypatch.setattr("app.services.oauth.settings.GOOGLE_CLIENT_SECRET", SecretStr(""))
    with pytest.raises(HTTPException) as error:
        service.authorization_url("google")
    assert error.value.status_code == 503
