from app.core.errors import DomainError


class InsufficientGoldError(DomainError):
    """Raised when user does not have enough gold to spend"""
    pass


class ProgressNotFoundError(DomainError):
    """
    Raised when progression document is not found. Used as safe-guard, should not trigger.
    """
    pass
