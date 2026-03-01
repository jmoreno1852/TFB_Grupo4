from datetime import datetime
from typing import List, Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import UpdateOne

from app.shop.domain.entities import ShopListing
from app.shop.domain.ports import ShopRotationRepository
from app.shop.persistence.mongo.mapper import doc_to_listing, listing_to_doc


class MongoShopRotationRepository(ShopRotationRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["shop_rotation"]

    async def ensure_initialized(self) -> None:
        """
        Ensure indexes to ensure a unique item_id per object in rotation.
        """
        await self._collection.create_index("item_id", unique=True)

    async def is_initialized(self) -> bool:
        return await self._collection.count_documents({}) > 0

    async def list_listings(self) -> List[ShopListing]:
        cursor = self._collection.find({})
        return [doc_to_listing(doc) async for doc in cursor]

    async def get_listing(self, item_id: str) -> Optional[ShopListing]:
        doc = await self._collection.find_one({"item_id": item_id})
        if doc is None:
            return None
        return doc_to_listing(doc)

    async def upsert_listings(self, listings: List[ShopListing]) -> None:
        ops = []
        for listing in listings:
            doc = listing_to_doc(listing)
            ops.append(
                UpdateOne(
                    {"item_id": listing.item_id},
                    {"$set": doc},
                    upsert=True,
                )
            )

        if not ops:
            return

        await self._collection.bulk_write(ops)

    async def rotate_if_needed(self, now: datetime) -> None:
        """
        This function only checks if there are expired listings, in case there are, listings are deleted. Rotations is triggered when checking the initialization of the shop rotation.
        """
        expired_count = await self._collection.count_documents({"available_to": {"$lt": now}})
        if expired_count > 0:
            await self._collection.delete_many({})
