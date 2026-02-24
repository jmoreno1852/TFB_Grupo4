from functools import lru_cache

from app.database import get_db

from app.shop.domain.services import ShopService
#Import Defined Gateways through ports
from app.shop.domain.ports import ItemCatalogGateway, ProgressionGateway, InventoryGateway

#Import repositories
from app.shop.persistence.mongo.repository import MongoShopRotationRepository

#Import needed services to build gateways
from app.inventory.domain.services import CatalogService, InventoryService
from app.progression.domain.services import ProgressionService
from app.inventory.domain.errors import ItemNotFoundInCatalogError

#Import needed builders from DI of other modules to build gateways with their services
from app.inventory.dependency_injection.providers import build_catalog_service, build_inventory_service

from app.progression.dependency_injection.providers import build_progression_service


class ItemCatalogServiceGateway(ItemCatalogGateway):
    """
    ItemCatalogGateway implementation backed by Inventory CatalogService.
    """

    def __init__(self, catalog_service: CatalogService):
        self.catalog_service = catalog_service

    async def get_item(self, item_id: str):
        try:
            return await self.catalog_service.get_catalog_item(item_id=item_id)
        except ItemNotFoundInCatalogError:
            return None

    async def list_items(self):
        return await self.catalog_service.list_catalog_items()


class ProgressionServiceGateway(ProgressionGateway):
    """
    ProgressionGateway implementation backed by ProgressionService.
    """

    def __init__(self, progression_service: ProgressionService):
        self.progression_service = progression_service

    async def spend_gold(self, user_id: str, amount: int) -> None:
        
        await self.progression_service.spend_gold(user_id=user_id, amount=amount)


class InventoryServiceGateway(InventoryGateway):
    """
    InventoryGateway implementation backed by InventoryService.
    """

    def __init__(self, inventory_service: InventoryService):
        self.inventory_service = inventory_service

    async def add_item(self, user_id: str, item_id: str, quantity: int) -> None:
        await self.inventory_service.add_item_to_inventory(
            user_id=user_id,
            item_id=item_id,
            quantity=quantity,
        )


@lru_cache(maxsize=1)
def build_shop_rotation_repository() -> MongoShopRotationRepository:
    """
    Build and return MongoShopRotationRepository instance.
    """
    return MongoShopRotationRepository(get_db())


@lru_cache(maxsize=1)
def build_item_catalog_gateway() -> ItemCatalogGateway:
    """
    Build and return ItemCatalogGateway implementation.
    """
    return ItemCatalogServiceGateway(
        catalog_service=build_catalog_service(),
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
def build_inventory_gateway() -> InventoryGateway:
    """
    Build and return InventoryGateway implementation.
    """
    return InventoryServiceGateway(
        inventory_service=build_inventory_service(),
    )


@lru_cache(maxsize=1)
def build_shop_service() -> ShopService:
    """
    Build and return ShopService instance.
    """
    return ShopService(
        shop_repository=build_shop_rotation_repository(),
        catalog_gateway=build_item_catalog_gateway(),
        progression_gateway=build_progression_gateway(),
        inventory_gateway=build_inventory_gateway(),
    )


def clear_caches() -> None:
    """
    Clear lru_cache for DI providers. Useful in testing when FastAPI TestClient recreates the app multiple times.
    """
    build_shop_rotation_repository.cache_clear()
    build_item_catalog_gateway.cache_clear()
    build_progression_gateway.cache_clear()
    build_inventory_gateway.cache_clear()
    build_shop_service.cache_clear()