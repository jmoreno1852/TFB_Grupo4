from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from app.shop.domain.entities import ShopListing
from app.inventory.domain.entities import Item


class ShopRotationRepository(ABC):
    @abstractmethod
    async def list_listings(self) -> List[ShopListing]:
        """
        List items currently in the shop rotation.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_listing(self, item_id: str) -> Optional[ShopListing]:
        """
        Retrieve a specific listing from the current shop rotation by item_id.
        """
        raise NotImplementedError

    @abstractmethod
    async def upsert_listings(self, listings: List[ShopListing]) -> None:
        """
        Insert or update the current shop rotation listings.
        """
        raise NotImplementedError

    @abstractmethod
    async def is_initialized(self) -> bool:
        """
        Returns True if the shop rotation already contains listings.
        Used to determine if lazy initialization is required.
        """
        raise NotImplementedError

    @abstractmethod
    async def rotate_if_needed(self, now: datetime) -> None:
        """
        Rotates shop listings if rotation window has expired.
        """
        raise NotImplementedError


class ItemCatalogGateway(ABC):
    @abstractmethod
    async def get_item(self, item_id: str) -> Optional[Item]:
        """
        Retrieve an item from the global catalog, functionality from inventory module.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_items(self) -> List[Item]:
        """
        List all items from the global catalog, functionality from inventory module.
        """
        raise NotImplementedError


class ProgressionGateway(ABC):
    @abstractmethod
    async def spend_gold(self, user_id: str, amount: int) -> None:
        """
        Decrease gold from user's progression, used for purchases.
        """
        raise NotImplementedError


class InventoryGateway(ABC):
    @abstractmethod
    async def add_item(self, user_id: str, item_id: str, quantity: int) -> None:
        """
        Add an item to the user's inventory, functionality comes from inventory module.
        """
        raise NotImplementedError