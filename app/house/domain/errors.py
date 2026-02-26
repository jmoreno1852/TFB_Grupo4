from app.core.errors import DomainError


class HouseLockedError(DomainError):
    """Raised when user has no unlocked rooms yet."""
    pass


class RoomLockedError(DomainError):
    """Raised when trying to place furniture in a locked room."""
    pass


class InvalidPlacementError(DomainError):
    """Raised when room_index or slot_index is invalid."""
    pass


class ItemNotOwnedError(DomainError):
    """Raised when user does not own the specified item."""
    pass


class InvalidItemTypeError(DomainError):
    """Raised when item is not of type 'furniture'."""
    pass