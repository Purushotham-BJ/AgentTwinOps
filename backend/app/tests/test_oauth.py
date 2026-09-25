import pytest
from fastapi import HTTPException

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
