# app/users/domain/errors.py
from app.core.errors import DomainError


class UserNotFoundError(DomainError):
    """Raised when user profile not found."""
    pass


class InvalidUpdateError(DomainError):
    """Raised when an update request violates validation rules at domain level."""
    pass