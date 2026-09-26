"""AI-service test configuration.

pytest-asyncio is configured in auto mode so every async test function
is treated as a coroutine test without needing an explicit marker.
"""
import pytest


# Tell pytest-asyncio to discover async tests automatically
def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "asyncio: mark test as asyncio (auto-applied by pytest-asyncio)",
    )
