from app.core.errors import DomainError


class ItemNotOwnedError(DomainError):
    """Raised when user tries to use or equip an item they do not own. Should not happen, added as safeguard"""
    pass


class SlotInvalidError(DomainError):
    """Raised when an invalid equipment slot is provided."""
    pass


class ItemNotFoundInCatalogError(DomainError):
    """Raised when an item does not exist in the global catalog."""
    pass


class ItemNotEquippableError(DomainError):
    """Raised when trying to equip an item that is not equippable or incompatible with the slot."""
    pass

