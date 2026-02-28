from functools import lru_cache

from app.database import get_db

from app.house.domain.services import HouseService
from app.house.domain.ports import InventoryGateway, ProgressionGateway

from app.house.persistence.mongo.repository import MongoHouseRepository

#Import services from other modules
from app.inventory.domain.services import InventoryService
from app.progression.domain.services import ProgressionService

#Import builders from other modules
from app.inventory.dependency_injection.providers import build_inventory_service
from app.progression.dependency_injection.providers import build_progression_service


class InventoryServiceGateway(InventoryGateway):
    """
    InventoryGateway implementation backed by InventoryService.
    """

    def __init__(self, inventory_service: InventoryService):
        self.inventory_service = inventory_service

    async def get_user_item(self, user_id: str, item_id: str):

        return await self.inventory_service.get_user_item(user_id=user_id, item_id=item_id)

    async def consume_item(self, user_id: str, item_id: str, amount: int = 1) -> None:
        
        return await self.inventory_service.consume_item(user_id=user_id, item_id=item_id, amount=amount)
    
    async def grant_item(self, user_id: str, item_id: str, amount: int = 1) -> None:
        return await self.inventory_service.grant_item(user_id=user_id, item_id=item_id, amount=amount) 
        

class ProgressionServiceGateway(ProgressionGateway):
    """
    ProgressionGateway implementation backed by ProgressionService.
    """

    def __init__(self, progression_service: ProgressionService):
        self.progression_service = progression_service

    async def get_level(self, user_id: str) -> int:
        return await self.progression_service.get_level(user_id=user_id)


@lru_cache(maxsize=1)
def build_house_repository() -> MongoHouseRepository:
    """
    Build and return MongoHouseRepository instance.
    """
    return MongoHouseRepository(get_db())


@lru_cache(maxsize=1)
def build_inventory_gateway() -> InventoryGateway:
    """
    Build and return InventoryGateway implementation.
    """
    return InventoryServiceGateway(
        inventory_service=build_inventory_service(),
    )


@lru_cache(maxsize=1)
def build_progression_gateway() -> ProgressionGateway:
    """
    Build and return ProgressionGateway implementation.
    """
    return ProgressionServiceGateway(
        progression_service=build_progression_service(),
    )


@lru_cache(maxsize=1)
def build_house_service() -> HouseService:
    """
    Build and return HouseService instance.
    """
    return HouseService(
        house_repository=build_house_repository(),
        inventory_gateway=build_inventory_gateway(),
        progression_gateway=build_progression_gateway(),
    )


def clear_caches() -> None:
    """
    Clear lru_cache for DI providers. Useful in testing when FastAPI TestClient recreates the app multiple times.
    """
    build_house_repository.cache_clear()
    build_inventory_gateway.cache_clear()
    build_progression_gateway.cache_clear()
    build_house_service.cache_clear()