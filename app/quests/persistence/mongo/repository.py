from datetime import datetime, timezone
from typing import Any, Iterable, Optional

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.quests.domain.entities import Quest, UserQuest
from app.quests.domain.ports import QuestCatalogRepository, UserQuestRepository
from app.quests.persistence.mongo.mapper import (
    doc_to_quest,
    quest_to_doc,
    doc_to_user_quest,
    user_quest_to_doc,
)


class QuestCatalogMongoRepository(QuestCatalogRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["quests"]

    async def list_active_by_guild(self, guild_id: str) -> Iterable[Quest]:
        """List active quests in a guild"""
        cursor = self._collection.find({"guild_id": guild_id, "is_active": True})
        return [doc_to_quest(doc) async for doc in cursor]

    async def get_by_id(self, quest_id: str) -> Optional[Quest]:
        """Get Quest catalog by ID"""
        try:
            oid = ObjectId(quest_id)
        except Exception:
            return None

        doc = await self._collection.find_one({"_id": oid})
        if doc is None:
            return None
        return doc_to_quest(doc)

    async def get_many_by_ids(self, quest_ids: list[str]) -> Iterable[Quest]:
        """Get multiple quests by their ids, used to merge catalog data into user quests response"""
        oids: list[ObjectId] = []
        for qid in quest_ids:
            try:
                oids.append(ObjectId(qid))
            except Exception:
                continue

        if not oids:
            return []

        cursor = self._collection.find({"_id": {"$in": oids}})
        return [doc_to_quest(doc) async for doc in cursor]

    async def create_quest(self, quest: Quest) -> Quest:
        """Create a quest for a specific guild catalog at persistence layer"""
        created = await self._collection.insert_one(quest_to_doc(quest))
        doc = await self._collection.find_one({"_id": created.inserted_id})
        return doc_to_quest(doc)

    async def update_quest(self, quest_id: str, updates: dict[str, Any]) -> Optional[Quest]:
        """Update a quest in a guild's catalog"""
        try:
            oid = ObjectId(quest_id)
        except Exception:
            return None

        updates = dict(updates)
        updates["updated_at"] = datetime.now(timezone.utc)  

        result = await self._collection.update_one({"_id": oid}, {"$set": updates})
        if result.matched_count == 0:
            return None

        doc = await self._collection.find_one({"_id": oid})
        if doc is None:
            return None
        return doc_to_quest(doc)

    async def delete_quest(self, quest_id: str) -> None:
        """Delete quest from a guild's catalog at persistence layer"""
        try:
            oid = ObjectId(quest_id)
        except Exception:
            return None

        await self._collection.delete_one({"_id": oid})

    async def ensure_indexes(self):
        await self._collection.create_index([("guild_id", 1), ("is_active", 1)])


class UserQuestMongoRepository(UserQuestRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["user_quests"]

    async def count_active(self, user_id: str, guild_id: str) -> int:
        """Count active quests from a specific guild assigned to a user """
        return await self._collection.count_documents(
            {"user_id": user_id, "guild_id": guild_id, "status": "active"}
        )

    async def list_active_by_user(self, user_id: str) -> Iterable[UserQuest]:
        """List active quests from all guilds assigned to a user"""
        cursor = self._collection.find({"user_id": user_id, "status": "active"})
        return [doc_to_user_quest(doc) async for doc in cursor]

    async def list_active_by_user_guild(self, user_id: str, guild_id: str) -> Iterable[UserQuest]:
        """List active quests from a specific guild assigned to a user"""
        cursor = self._collection.find(
            {"user_id": user_id, "guild_id": guild_id, "status": "active"}
        )
        return [doc_to_user_quest(doc) async for doc in cursor]

    async def list_recent_completed(self, user_id: str, guild_id: str, limit: int = 10) -> Iterable[UserQuest]:
        """List recently completer quests for a specific user in a guild, default limit at 10"""
        cursor = self._collection.find({"user_id": user_id, "guild_id": guild_id, "status": "completed"}).sort("completed_at", -1).limit(limit)
        return [doc_to_user_quest(doc) async for doc in cursor]

    async def get_active_assignment(self, user_id: str, quest_id: str) -> Optional[UserQuest]:
        """Get active quest assigned to a user by quest_ID, used to validate if a quest is already assigned and active for a user"""
        doc = await self._collection.find_one({"user_id": user_id, "quest_id": quest_id, "status": "active"})
        if doc is None:
            return None
        return doc_to_user_quest(doc)

    async def get_completed_assignment(self, user_id: str, quest_id: str) -> Optional[UserQuest]:
        """Get completed quest assigned to a user by quest_ID, used to validate if a quest is already assigned and completed for a user"""
        doc = await self._collection.find_one({"user_id": user_id, "quest_id": quest_id, "status": "completed"})
        if doc is None:
            return None
        return doc_to_user_quest(doc)

    async def create_assignment(self, user_quest: UserQuest) -> UserQuest:
        """Assign a quest to a user at persistence layer"""
        await self._collection.insert_one(user_quest_to_doc(user_quest))
        return user_quest

    async def mark_completed(self, user_id: str, quest_id: str, completed_at: datetime) -> None:
        """Mark an existing quest as completed for a specific user at persistence layer"""
        await self._collection.update_one(
            {"user_id": user_id, "quest_id": quest_id, "status": "active"},
            {"$set": {"status": "completed", "completed_at": completed_at}},
        )

    async def ensure_indexes(self):
        # Ensuring uniqueness for user, guild, quest relationship
        await self._collection.create_index(
            [("user_id", 1), ("guild_id", 1), ("quest_id", 1)],
            unique=True,
        )

        # Inde to speed up user quest listing and the boostrap 
        await self._collection.create_index([("user_id", 1), ("status", 1)])
        await self._collection.create_index([("user_id", 1), ("guild_id", 1), ("status", 1)])

        # Index to speed up recent completed queries
        await self._collection.create_index([("user_id", 1), ("guild_id", 1), ("completed_at", -1)])
