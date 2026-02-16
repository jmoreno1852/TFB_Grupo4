from abc import ABC, abstractmethod
from typing import List

from app.inventory.domain.entities import Inventory, Item


class InventoryRepository(ABC):
    @abstractmethod
    async def get_by_user(self, user_id: str) -> Inventory:
        """
        Retrieve inventory related to a user.
        Lazy initialization impleemnted if none is retrieved.
        """
        raise NotImplementedError

    @abstractmethod
    async def update_inventory(self, inventory: Inventory) -> None:
        """
        Persist state of inventory, needed for actions that modify inventory like equipping items.
        """
        raise NotImplementedError

    @abstractmethod
    async def add_item(self, user_id: str, item_id: str, quantity: int) -> Inventory:
        """
        Add an item to the user's inventory.
        """
        raise NotImplementedError

    @abstractmethod
    async def remove_item(self, user_id: str, item_id: str, quantity: int) -> Inventory:
        """
        Remove an item from the user's inventory. Intended for management actions and future features like selling items.
        """
        raise NotImplementedError


class ItemCatalogRepository(ABC):
    @abstractmethod
    async def get_item(self, item_id: str) -> Item:
        """
        Retrieve an item from the global catalog.
        Raises ItemNotFoundInCatalogError if not found.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_items(self) -> List[Item]:
        """
        List all items from the global catalog.
        """
        raise NotImplementedError

    @abstractmethod
    async def upsert_items(self, items: List[Item]) -> None:
        """
        Insert or update multiple items in the catalog.
        Used for administrative tasks like seeding or updating catalog data.
        """
        raise NotImplementedError

    @abstractmethod
    async def is_initialized(self) -> bool:
        """
        Returns True if the catalog already contains items.
        Used to determine if seed initialization is required.
        """
        raise NotImplementedError
