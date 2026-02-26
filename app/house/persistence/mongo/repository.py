from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.house.domain.entities import House
from app.house.domain.ports import HouseRepository
from app.house.persistence.mongo.mapper import doc_to_house, house_to_doc


class MongoHouseRepository(HouseRepository):
    """
    Mongo implementation for HouseRepository.

    """

    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["houses"]

    async def get_by_user(self, user_id: str) -> Optional[House]:
        doc = await self._collection.find_one({"user_id": user_id})
        if doc is None:
            return None
        return doc_to_house(doc)

    async def save(self, house: House) -> None:
        doc = house_to_doc(house)

        await self._collection.update_one(
            {"user_id": house.user_id},
            {"$set": doc},
            upsert=True,
        )

    async def ensure_indexes(self):
        # Ensure 1 house per user 
        await self._collection.create_index("user_id", unique=True)
