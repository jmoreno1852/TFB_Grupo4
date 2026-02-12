from app.core.errors import DomainError


class QuestNotFoundError(DomainError):
    """Raised when quest does not exist in quest catalog"""
    pass


class QuestAlreadyCompletedError(DomainError):
    """Raised when user tries to complete a quest  that already has the complete status"""
    pass


class QuestNotAssignedError(DomainError):
    """Raised when user tries to complete a quest not assigned. This should not happen but acts as a safeguard"""
    pass


class QuestUpdateError(DomainError):
    """Raised when there is a failure during quest update"""
    pass


class QuestDeleteError(DomainError):
    """Raised when there is a failure during quest deletion"""
    pass
