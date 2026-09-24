"""Exception package — custom hierarchy and global handlers."""

from app.exceptions.base import (
    AppException,
    ConflictException,
    NotFoundException,
    ValidationException,
)
from app.exceptions.handlers import register_exception_handlers

__all__ = [
    "AppException",
    "ConflictException",
    "NotFoundException",
    "ValidationException",
    "register_exception_handlers",
]
