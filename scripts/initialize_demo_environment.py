"""Initialize the shared onboarding demo environment for an existing user."""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
from pathlib import Path

from sqlalchemy import select

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.database.session import async_session_factory  # noqa: E402
from app.models.user import User  # noqa: E402
from app.services.demo_environment import initialize_default_demo_environment  # noqa: E402


async def initialize(email: str) -> None:
    async with async_session_factory() as session:
        user = await session.scalar(select(User).where(User.email == email.strip().lower()))
        if not user:
            raise SystemExit(f"User not found: {email}")
        initialized = await initialize_default_demo_environment(session, user.id)
        logging.info("Demo environment %s", "initialized" if initialized else "already ready")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", required=True, help="Existing account email")
    args = parser.parse_args()
    asyncio.run(initialize(args.email))


if __name__ == "__main__":
    main()
