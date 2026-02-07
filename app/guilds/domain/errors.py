from app.core.errors import DomainError

class GuildNotFoundError(DomainError):
    """Raised when guild does not exist."""
    pass


class AlreadyInGuildError(DomainError):
    """Raised when user already belongs to a guild"""
    pass


class NotInGuildError(DomainError):
    """Raised when tries to leave a guild they are not part of"""
    pass


class GuildAlreadyExistsError(DomainError):
    """Raised when trying to create already existing guild"""
    pass


class InvalidGuildNameError(DomainError):
    """Raised when a guild name is invalid"""
    pass

class GuildHasMembersError(DomainError):
    """Raised when deleting a guild that have members"""
    pass

