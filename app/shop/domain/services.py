import random
from datetime import datetime, timezone, time, timedelta
from typing import List, Optional

from app.shop.domain.entities import ShopItemView, ShopListing
from app.shop.domain.errors import ShopItemNotFoundError, CatalogItemNotFoundError
from app.shop.domain.ports import (
    ShopRotationRepository,
    ItemCatalogGateway,
    ProgressionGateway,
    InventoryGateway,
)


class ShopService:
    def __init__(
        self,
        shop_repository: ShopRotationRepository,
        catalog_gateway: ItemCatalogGateway,
        progression_gateway: ProgressionGateway,
        inventory_gateway: InventoryGateway,
        rotation_size: int = 5,
    ):
        self.shop_repository = shop_repository
        self.catalog_gateway = catalog_gateway
        self.progression_gateway = progression_gateway
        self.inventory_gateway = inventory_gateway
        self.rotation_size = rotation_size

    async def list_items(self) -> List[ShopItemView]:
        await self.ensure_rotation_initialized()

        listings = await self.shop_repository.list_listings()
        views: List[ShopItemView] = []

        for listing in listings:
            item = await self.catalog_gateway.get_item(listing.item_id)
            if item is None:
                raise CatalogItemNotFoundError(f"Catalog item not found for item_id={listing.item_id}")              
            views.append(
                ShopItemView(
                    id=item.id,
                    name=item.name,
                    description=item.description,
                    type=item.type,
                    equippable_slot=item.equippable_slot,
                    value=item.value,
                )
            )

        return views

    async def purchase(self, user_id: str, item_id: str, quantity: int = 1,) -> None:
        user_id_norm = user_id.strip()
        item_id_norm = item_id.strip()

        if quantity <= 0:
            raise ValueError("quantity must be > 0")

        await self.ensure_rotation_initialized()

        listing = await self.shop_repository.get_listing(item_id_norm)
        if listing is None:
            raise ShopItemNotFoundError("Item not found in current shop rotation.")

        item = await self.catalog_gateway.get_item(item_id_norm)
        if item is None:
            raise CatalogItemNotFoundError("Catalog item not found.")

        total_price = item.value * quantity
        #Spend gold from user progression
        await self.progression_gateway.spend_gold(user_id_norm, total_price)
        #Add item from user inventory
        await self.inventory_gateway.add_item(user_id_norm, item_id_norm, quantity)

    async def rotate_shop(self, now: Optional[datetime] = None) -> None:
        now_utc = now or datetime.now(timezone.utc)
        await self.shop_repository.rotate_if_needed(now_utc)

    async def ensure_rotation_initialized(self) -> None:
        if await self.shop_repository.is_initialized():
            await self.rotate_shop()
            return

        catalog_items = await self.catalog_gateway.list_items()
        if not catalog_items:
            raise CatalogItemNotFoundError("Catalog is empty; cannot initialize shop.")

        chosen = random.sample(
            catalog_items, k=self.rotation_size
        )

        now_utc = datetime.now(timezone.utc)
        day_start = datetime.combine(now_utc.date(), time(0, 0, 0), tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1) - timedelta(microseconds=1)

        listings = [
            ShopListing(
                item_id=item.id,
                available_from=day_start,
                available_to=day_end,
            )
            for item in chosen
        ]

        await self.shop_repository.upsert_listings(listings)