"""Password policy shared by registration and password creation flows."""
from __future__ import annotations

import re

MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128
SPECIAL_CHARACTERS = r"""!@#$%^&*()_+\-=\[\]{}:;'"<>,.?/\\|`~"""
_SPECIAL_CHARACTER_PATTERN = re.compile(f"[{SPECIAL_CHARACTERS}]")
_COMMON_WEAK_PASSWORDS = frozenset({"short@1a"})


def validate_password_strength(password: str) -> str:
    """Validate and return a password without logging or transforming it."""
    if password.casefold() in _COMMON_WEAK_PASSWORDS:
        raise ValueError("Password is too weak; choose a less predictable password.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError("Password must be at least 8 characters long.")
    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError("Password must not exceed 128 characters.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must contain at least one lowercase letter.")
    if not re.search(r"[0-9]", password):
        raise ValueError("Password must contain at least one number.")
    if not _SPECIAL_CHARACTER_PATTERN.search(password):
        raise ValueError("Password must contain at least one special character.")
    return password
