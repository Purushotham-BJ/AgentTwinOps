"""Structured logging configuration.

Provides two output formats controlled by ``Settings.LOG_FORMAT``:
  * **console** — human-readable, coloured output for local development.
  * **json** — machine-parseable JSON lines for production log aggregators.
"""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.config.settings import Settings


def setup_logging(settings: Settings) -> None:
    """Configure the root logger based on application settings.

    Parameters
    ----------
    settings:
        The validated application settings instance (injected).
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # ── Formatter ───────────────────────────────────────────────
    if settings.LOG_FORMAT == "json":
        fmt = (
            '{"time":"%(asctime)s","level":"%(levelname)s",'
            '"logger":"%(name)s","message":"%(message)s"}'
        )
    else:
        fmt = (
            "\033[2m%(asctime)s\033[0m "
            "%(levelname)-8s "
            "\033[36m%(name)s\033[0m "
            "%(message)s"
        )

    formatter = logging.Formatter(fmt, datefmt="%Y-%m-%d %H:%M:%S")

    # ── Handler ─────────────────────────────────────────────────
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # ── Root logger ─────────────────────────────────────────────
    root = logging.getLogger()
    root.setLevel(log_level)

    # Avoid duplicate handlers when reloading (uvicorn --reload)
    root.handlers.clear()
    root.addHandler(handler)

    # ── Silence noisy third-party loggers ───────────────────────
    for noisy in ("uvicorn.access", "httpcore", "httpx"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    logging.getLogger(__name__).debug(
        "Logging configured: level=%s format=%s",
        settings.LOG_LEVEL,
        settings.LOG_FORMAT,
    )
