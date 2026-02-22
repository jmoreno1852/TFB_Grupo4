from app.core.errors import DomainError

#error for insufficient gold not implemented here as that error lives in progression domain
class ShopItemNotFoundError(DomainError):
    """Raised when an item is not part of the current shop rotation."""
    pass


class CatalogItemNotFoundError(DomainError):
    """Raised when a shop listing references a non-existing catalog item."""
    pass


class ShopNotInitializedError(DomainError):
    """Raised when the shop rotation has not been initialized yet."""
    pass