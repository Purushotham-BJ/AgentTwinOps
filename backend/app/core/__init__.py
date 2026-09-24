"""Core package — application factory, lifespan, and logging."""

from app.core.factory import create_app

__all__ = ["create_app"]
