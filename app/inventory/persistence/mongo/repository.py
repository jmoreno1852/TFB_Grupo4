from datetime import datetime, timezone
from typing import List

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import UpdateOne

from app.inventory.domain.entities import Inventory, Item, InventoryItem
from app.inventory.domain.ports import InventoryRepository, ItemCatalogRepository
from app.inventory.domain.errors import ItemNotFoundInCatalogError
from app.inventory.persistence.mongo.mapper import (
    doc_to_inventory,
    inventory_to_doc,
    doc_to_item,
    item_to_doc,
)


# InventoryRepository implementation for MongoDB
class MongoInventoryRepository(InventoryRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["inventories"]

    async def get_by_user(self, user_id: str) -> Inventory:
        """
        Retrieve inventory related to a user.
        Lazy initialization implemented if none is retrieved.
        """
        now_utc = datetime.now(timezone.utc)

        await self._collection.update_one(
            {"user_id": user_id},
            {
                "$setOnInsert": {
                    "user_id": user_id,
                    "items": [],
                    "equipment": {
                        "weapon": None,
                        "helmet": None,
                        "armor": None,
                        "leg_armor": None,
                        "boots": None,
                        "accessory": None,
                    },
                    "created_at": now_utc,
                    "updated_at": None,
                }
            },
            upsert=True,
        )

        doc = await self._collection.find_one({"user_id": user_id})

        return doc_to_inventory(doc)

    async def update_inventory(self, inventory: Inventory) -> None:
        """
        Persist state of inventory.
        """
        now_utc = datetime.now(timezone.utc)

        doc = inventory_to_doc(inventory)

        doc["updated_at"] = now_utc

        await self._collection.update_one(
            {"user_id": inventory.user_id},
            {"$set": doc},
            upsert=True,
        )
    async def ensure_indexes(self) -> None:
        """
        Ensure indexes, unique inventory per user
        """
        await self._collection.create_index("user_id", unique=True)



# ItemCatalogRepository implementation for MongoDB
class MongoItemCatalogRepository(ItemCatalogRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["item_catalog"]

    async def is_initialized(self) -> bool:
        return await self._collection.count_documents({}) > 0

    async def upsert_items(self, items: List[Item]) -> None:
        ops = []
        for item in items:
            doc = item_to_doc(item)
            ops.append(
                UpdateOne(
                    {"_id": item.id},
                    {"$set": doc},
                    upsert=True,
                )
            )

        if not ops:
            return

        await self._collection.bulk_write(ops)

    async def list_items(self) -> List[Item]:
        cursor = self._collection.find({})
        return [doc_to_item(doc) async for doc in cursor]

    async def get_item(self, item_id: str) -> Item:
        doc = await self._collection.find_one({"_id": item_id})
        if doc is None:
            raise ItemNotFoundInCatalogError("Item not found in catalog.")
        return doc_to_item(doc)


