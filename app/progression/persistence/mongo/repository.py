from datetime import datetime, timezone

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.progression.domain.entities import Progression
from app.progression.domain.ports import ProgressionRepository
from app.progression.domain.errors import InsufficientGoldError
from app.progression.persistence.mongo.mapper import doc_to_progression, progression_to_doc


class MongoProgressionRepository(ProgressionRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["progression"]

    async def get_by_user(self, user_id: str) -> Progression:
        """
        Get Progression by user_id. Implementation with lazy initialization.
        """
        now_utc = datetime.now(timezone.utc)
        #Using update one with upsert to ensure creation if not exists
        #Using setOnInsert to avoid overwriting existing progression if it already exists.
        await self._collection.update_one(
            {"user_id": user_id},
            {
                "$setOnInsert": {
                    "user_id": user_id,
                    "level": 1,
                    "xp": 0,
                    "gold": 0,
                    "stats": {"strength": 0, "focus": 0, "resilience": 0},
                    "created_at": now_utc,
                    "updated_at": None,
                }
            },
            upsert=True,
        )

        doc = await self._collection.find_one({"user_id": user_id})

        return doc_to_progression(doc)

    async def update_progression(self, progression: Progression) -> None:
        """
        Persist changes in progression in persistence layer.
        """
        now_utc = datetime.now(timezone.utc)

        doc = progression_to_doc(progression)
        doc["updated_at"] = now_utc

        await self._collection.update_one(
            {"user_id": progression.user_id},
            {"$set": doc},
        )

    async def spend_gold(self, user_id: str, amount: int) -> Progression:
        """
        Function to decrease gold from user progression, used by Shop module.
        """
        now_utc = datetime.now(timezone.utc)

        result = await self._collection.update_one(
            #We compare gold in query to the gold the user has, in case of being greater or equial the ammount is decreased
            #If ammount cant be decreased because user has less gold, we raise error
            {"user_id": user_id, "gold": {"$gte": amount}},
            {"$inc": {"gold": -amount}, "$set": {"updated_at": now_utc}},
        )
        #If the query does not found a doc with user_id with enough gold it means the user can't afford the operation
        if result.matched_count == 0:
            raise InsufficientGoldError("Not enough gold to complete the operation.")

        doc = await self._collection.find_one({"user_id": user_id})

        return doc_to_progression(doc)

    async def ensure_initialized(self):
        # Ensure one progression per user
        await self._collection.create_index("user_id", unique=True)
