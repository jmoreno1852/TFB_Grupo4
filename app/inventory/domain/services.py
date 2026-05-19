from dataclasses import replace
from datetime import datetime, timezone
from typing import List, Optional

from app.inventory.domain.entities import Item, Inventory, InventoryItem
from app.inventory.domain.ports import InventoryRepository, ItemCatalogRepository
from app.inventory.domain.errors import (
    ItemNotOwnedError,
    SlotInvalidError,
    ItemNotEquippableError,
)


# Seed for Catalog MVP implementation, this could be later intialized from a json file 
DEFAULT_ITEMS_SEED: List[Item] = [
    Item(
        id="rusty_sword",
        name="Rusty Sword",
        description="A basic sword. Better than nothing.",
        type="weapon",
        equippable_slot="weapon",
        value=25,
    ),
    Item(
        id="iron_helmet",
        name="Iron Helmet",
        description="A sturdy helmet.",
        type="armor",
        equippable_slot="helmet",
        value=30,
    ), 
    Item(
        id="simple_ring",
        name="Simple Ring",
        description="A small accessory, fashion is everything, right?.",
        type="accessory",
        equippable_slot="accessory",
        value=15,
    ),
    Item(
        id="leather_armor",
        name="Leather Armor",
        description="Simple armor crafted with decent leather.",
        type="armor",
        equippable_slot="armor",
        value=40,
    ),
    Item(
        id="leather_leg_armor",
        name="Leather Leg Armor",
        description="Basic leg protection.",
        type="armor",
        equippable_slot="leg_armor",
        value=35,
    ),
    Item(
        id="leather_boots",
        name="Leather Boots",
        description="Comfortable boots for daily walks.",
        type="armor",
        equippable_slot="boots",
        value=20,
    ), 
    Item(
        id="wooden_table",
        name="Wooden Table",
        description="A simple wooden table for your house.",
        type="furniture",
        equippable_slot=None,
        value=60,
    ),
    Item(
        id="cozy_bed",
        name="Cozy Bed",
        description="A comfortable bed to rest after adventures.",
        type="furniture",
        equippable_slot=None,
        value=120,
    ),
    Item(
        id="stone_fireplace",
        name="Stone Fireplace",
        description="Keeps your house warm and stylish.",
        type="furniture",
        equippable_slot=None,
        value=150,
    ),
    
]

class CatalogService:
    """
    Service for global item catalog operations.
    """

    def __init__(self, catalog_repository: ItemCatalogRepository):
        self.catalog_repository = catalog_repository

    async def ensure_catalog_initialized(self) -> None:
        initialized = await self.catalog_repository.is_initialized()
        if not initialized:
            await self.catalog_repository.upsert_items(DEFAULT_ITEMS_SEED)

    async def get_catalog_item(self, item_id: str) -> Item:
        item_id_norm = item_id.strip()

        await self.ensure_catalog_initialized()
        return await self.catalog_repository.get_item(item_id_norm)

    async def list_catalog_items(self) -> List[Item]:
        await self.ensure_catalog_initialized()
        return await self.catalog_repository.list_items()


class InventoryService:
    """
    Service for user inventory operation.
    """

    VALID_SLOTS = {
        "weapon",
        "helmet",
        "armor",
        "leg_armor",
        "boots",
        "accessory",
    }

    def __init__(
        self,
        inventory_repository: InventoryRepository,
        catalog_repository: ItemCatalogRepository,
    ):
        self.inventory_repository = inventory_repository
        self.catalog_repository = catalog_repository

    async def ensure_catalog_initialized(self) -> None:
        initialized = await self.catalog_repository.is_initialized()
        if not initialized:
            await self.catalog_repository.upsert_items(DEFAULT_ITEMS_SEED)

    async def get_inventory(self, user_id: str) -> Inventory:
        user_id_norm = user_id.strip()

        await self.ensure_catalog_initialized()
        return await self.inventory_repository.get_by_user(user_id_norm)

    async def add_item_to_inventory(self, user_id: str, item_id: str, quantity: int) -> Inventory:
        user_id_norm = user_id.strip()
        item_id_norm = item_id.strip()

        #Ensure that the quantity of the added item is at least 1
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")

        await self.ensure_catalog_initialized()

        # Check if item exists in catalog
        await self.catalog_repository.get_item(item_id_norm)  # raises ItemNotFoundInCatalogError

        inventory = await self.inventory_repository.get_by_user(user_id_norm)

        # Readable load-modify-update
        existing_item: Optional[InventoryItem] = None

        for owned_item in inventory.items:
            if owned_item.item_id == item_id_norm:
                existing_item = owned_item
                break

        if existing_item is None:
            updated_items = list(inventory.items) + [
                InventoryItem(item_id=item_id_norm, quantity=quantity)
            ]
        else:
            updated_items = [
                replace(owned_item, quantity=owned_item.quantity + quantity)
                if owned_item.item_id == item_id_norm
                else owned_item
                for owned_item in inventory.items
            ]

        updated_inventory = replace(
            inventory,
            items=updated_items,
            updated_at=datetime.now(timezone.utc),
        )
        await self.inventory_repository.update_inventory(updated_inventory)
        return updated_inventory

    async def equip_item(self, user_id: str, item_id: str, slot: str) -> Inventory:
        user_id_norm = user_id.strip()
        item_id_norm = item_id.strip()
        slot_norm = slot.strip()

        await self.ensure_catalog_initialized()
        #Simple check to make validation at domain level, not trusting client input
        if slot_norm not in self.VALID_SLOTS:
            raise SlotInvalidError("Invalid equipment slot.")

        #Load user's inventory to operate on
        inventory = await self.inventory_repository.get_by_user(user_id_norm)

        # Validate slot compatibility using catalog
        item = await self.catalog_repository.get_item(item_id_norm)  # raises ItemNotFoundInCatalogError
        if item.equippable_slot is None:
            raise ItemNotEquippableError("This item cannot be equipped.")
        if item.equippable_slot != slot_norm:
            raise ItemNotEquippableError("Item is not compatible with this slot.")
        
        #Check if slot already has an equipped item
        currently_equipped_item_id: Optional[str] = getattr(inventory.equipment, slot_norm)

        #Decrease new item quantity, and update in memory state
        inventory = self._consume_from_inventory(inventory, item_id_norm, 1)

        #If something was equipped before, return it to inventory
        if currently_equipped_item_id is not None:
            inventory = self._grant_to_inventory(inventory, currently_equipped_item_id, 1)


        new_equipment = replace(inventory.equipment, **{slot_norm: item_id_norm})
        updated_inventory = replace(
            inventory,
            equipment=new_equipment,
            updated_at=datetime.now(timezone.utc),
        )
        await self.inventory_repository.update_inventory(updated_inventory)
        return updated_inventory

    async def unequip_item(self, user_id: str, slot: str) -> Inventory:
        user_id_norm = user_id.strip()
        slot_norm = slot.strip()
        #Check to dont trust client input for slot values
        if slot_norm not in self.VALID_SLOTS:
            raise SlotInvalidError("Invalid equipment slot.")

        inventory = await self.inventory_repository.get_by_user(user_id_norm)
        #Get item id of current equipped item if there is one
        currently_equipped_item_id: Optional[str] = getattr(inventory.equipment, slot_norm)
        if currently_equipped_item_id is None:
            raise ItemNotEquippableError("No item equipped in this slot.")
        
        #Return equipped item to inventory
        inventory = self._grant_to_inventory(inventory, currently_equipped_item_id, 1)

        new_equipment = replace(inventory.equipment, **{slot_norm: None})
        updated_inventory = replace(
            inventory,
            equipment=new_equipment,
            updated_at=datetime.now(timezone.utc),
        )
        await self.inventory_repository.update_inventory(updated_inventory)
        return updated_inventory
    #Function defined for house module
    async def get_user_item(self, user_id: str, item_id: str):
        """
        Return minimal item info if owned by user, else None.
        """
        user_id_norm = user_id.strip()
        item_id_norm = item_id.strip()

        await self.ensure_catalog_initialized()

        inventory = await self.inventory_repository.get_by_user(user_id_norm)

        owns_item = any(
            owned_item.item_id == item_id_norm and owned_item.quantity > 0
            for owned_item in inventory.items
        )
        if not owns_item:
            return None

        # If user owns it, fetch item from catalog
        item = await self.catalog_repository.get_item(item_id_norm)  
        return {"item_id": item.id, "type": item.type}
    
    #Internal helper to remove item from inventory after equipping item
    def _consume_from_inventory(self, inventory: Inventory, item_id: str, amount: int = 1) -> Inventory:
        if amount < 1:
            raise ValueError("Amount must be >= 1.")

        existing_item: Optional[InventoryItem] = None
        for owned_item in inventory.items:
            if owned_item.item_id == item_id:
                existing_item = owned_item
                break

        if existing_item is None or existing_item.quantity < amount:
            raise ItemNotOwnedError("User does not own enough of this item.")

        new_quantity = existing_item.quantity - amount

        if new_quantity > 0:
            updated_items = [
                replace(owned_item, quantity=new_quantity)
                if owned_item.item_id == item_id
                else owned_item
                for owned_item in inventory.items
            ]
        else:
            updated_items = [
                owned_item
                for owned_item in inventory.items
                if owned_item.item_id != item_id
            ]

        return replace(inventory, items=updated_items)
    #Internal helper to add item to inventory after unequipping item
    def _grant_to_inventory(self, inventory: Inventory, item_id: str, amount: int = 1) -> Inventory:
        if amount < 1:
            raise ValueError("Amount must be >= 1.")
        existing_item: Optional[InventoryItem] = None
        for owned_item in inventory.items:
            if owned_item.item_id == item_id:
                existing_item = owned_item
                break

        if existing_item is None:
            updated_items = list(inventory.items) + [
                InventoryItem(item_id=item_id, quantity=amount)
            ]
        else:
            updated_items = [
                replace(owned_item, quantity=owned_item.quantity + amount)
                if owned_item.item_id == item_id
                else owned_item
                for owned_item in inventory.items
            ]

        return replace(inventory, items=updated_items)
    #Specific function for house module
    async def consume_item(self, user_id: str, item_id: str, amount: int = 1,) -> Inventory:
        user_id_norm = user_id.strip()
        item_id_norm = item_id.strip()

        await self.ensure_catalog_initialized()

        inventory = await self.inventory_repository.get_by_user(user_id_norm)

        updated_inventory = self._consume_from_inventory(
            inventory, item_id_norm, amount
        )

        updated_inventory = replace(
            updated_inventory,
            updated_at=datetime.now(timezone.utc),
        )

        await self.inventory_repository.update_inventory(updated_inventory)
        return updated_inventory
    #Specific function for house module
    async def grant_item(self, user_id: str, item_id: str, amount: int = 1,) -> Inventory:
        user_id_norm = user_id.strip()
        item_id_norm = item_id.strip()

        await self.ensure_catalog_initialized()
        await self.catalog_repository.get_item(item_id_norm)

        inventory = await self.inventory_repository.get_by_user(user_id_norm)

        updated_inventory = self._grant_to_inventory(
            inventory, item_id_norm, amount
        )

        updated_inventory = replace(
            updated_inventory,
            updated_at=datetime.now(timezone.utc),
        )

        await self.inventory_repository.update_inventory(updated_inventory)
        return updated_inventory