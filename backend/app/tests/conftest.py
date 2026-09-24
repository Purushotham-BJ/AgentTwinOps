import sys
import asyncio

# On Windows, asyncpg works more reliably with the SelectorEventLoop.
# Set this policy early so any module-level engines are created with the
# same loop type as test coroutines.
if sys.platform.startswith("win"):
    try:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    except Exception:
        pass
