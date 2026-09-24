"""FastAPI application entry point.

This module is the ASGI target for uvicorn::

    uvicorn app.main:app --reload

The app object is created via the application factory so all
configuration, middleware, and handler wiring happens in one place.
"""

from app.core.factory import create_app

app = create_app()
