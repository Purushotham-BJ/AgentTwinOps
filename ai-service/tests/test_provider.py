from app.agents.base import BaseAgent
from app.config.settings import settings


def test_gemini_is_selected_when_configured(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "test-gemini-key")
    monkeypatch.setattr(settings, "GEMINI_MODEL", "gemini-test-model")

    agent = BaseAgent("test")

    assert agent.llm is not None
    assert agent.llm.__class__.__name__ == "ChatGoogleGenerativeAI"


def test_unconfigured_gemini_uses_deterministic_fallback(monkeypatch):
    monkeypatch.setattr(settings, "AI_PROVIDER", "gemini")
    monkeypatch.setattr(settings, "GEMINI_API_KEY", "")

    agent = BaseAgent("test")

    assert agent.llm is None
