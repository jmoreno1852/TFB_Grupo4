from abc import ABC, abstractmethod
from typing import Optional

from app.house.domain.entities import House


class HouseRepository(ABC):

    @abstractmethod
    async def get_by_user(self, user_id: str) -> Optional[House]:
        """Get house entity by user_id"""
        raise NotImplementedError

    @abstractmethod
    async def save(self, house: House) -> None:
        """Persist house entity at persistence layer"""
        raise NotImplementedError


class InventoryGateway(ABC):
    #As we are implemeting only get_user_item, frontend will need to retrieve user inventory from /inventory/me
    #And get the item to POST, at Shop domain level we only validate that the item exists and its from the user that requested
    @abstractmethod
    async def get_user_item(self, user_id: str, item_id: str) -> Optional[dict]:
        """
        Returns item from user inventory by item_id
        """
        raise NotImplementedError
    @abstractmethod
    async def consume_item(self, user_id: str, item_id: str, amount: int = 1) -> None:
        """Decrease quantity of an item. Must fail if user doesn't have enough."""
        raise NotImplementedError
    
    @abstractmethod
    async def grant_item(self, user_id: str, item_id: str, amount: int = 1) -> None:
        """Increase quantity of an item."""
        raise NotImplementedError



class ProgressionGateway(ABC):
    @abstractmethod
    async def get_level(self, user_id: str) -> int:
        """Return user's current level"""
        raise NotImplementedError