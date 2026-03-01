from functools import lru_cache

from app.database import get_db

from app.inventory.persistence.mongo.repository import (
    MongoInventoryRepository,
    MongoItemCatalogRepository,
)
from app.inventory.domain.services import (
    InventoryService,
    CatalogService,
)
from app.inventory.domain.ports import InventoryRepository, ItemCatalogRepository

@lru_cache(maxsize=1)
def build_inventory_repository() -> InventoryRepository:
    """
    Build and return MongoInventoryRepository instance.
    """
    return MongoInventoryRepository(get_db())


@lru_cache(maxsize=1)
def build_item_catalog_repository() -> ItemCatalogRepository:
    """
    Build and return MongoItemCatalogRepository instance.
    """
    return MongoItemCatalogRepository(get_db())


@lru_cache(maxsize=1)
def build_inventory_service() -> InventoryService:
    """
    Build and return InventoryService instance.
    """
    return InventoryService(
        inventory_repository=build_inventory_repository(),
        catalog_repository=build_item_catalog_repository(),
    )


@lru_cache(maxsize=1)
def build_catalog_service() -> CatalogService:
    """
    Build and return CatalogService instance.
    """
    return CatalogService(
        catalog_repository=build_item_catalog_repository(),
    )


def clear_caches() -> None:
    """
    Clear lru_cache for DI providers. Useful in testing when FastAPI TestClient recreates the app multiple times.
    """
    build_inventory_service.cache_clear()
    build_catalog_service.cache_clear()
    build_inventory_repository.cache_clear()
    build_item_catalog_repository.cache_clear()