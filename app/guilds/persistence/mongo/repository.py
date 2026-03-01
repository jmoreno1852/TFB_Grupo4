from typing import Optional, Iterable

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from app.guilds.domain.entities import Guild, GuildMembership
from app.guilds.domain.ports import GuildRepository, MembershipRepository
from app.guilds.domain.errors import GuildAlreadyExistsError
from app.guilds.persistence.mongo.mapper import doc_to_guild, guild_to_doc, doc_to_membership, membership_to_doc


# GuildRepository implementation for MongoDB
class MongoGuildRepository(GuildRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["guilds"]

    async def list_all(self) -> Iterable[Guild]:
        pointer = self._collection.find({})
        return [doc_to_guild(doc) async for doc in pointer]

    async def get_by_id(self, guild_id: str) -> Optional[Guild]:
        # Validate if the string in guild_id is a valid ObjectId
        try:
            oid = ObjectId(guild_id)
        except Exception:
            return None

        doc = await self._collection.find_one({"_id": oid})
        if doc is None:
            return None
        return doc_to_guild(doc)

    async def get_by_name(self, name: str) -> Optional[Guild]:
        doc = await self._collection.find_one({"name": name})
        if doc is None:
            return None
        return doc_to_guild(doc)

    async def create(self, guild: Guild) -> Guild:
        # Ensure name is unique in Mongo
        try:
            created = await self._collection.insert_one(guild_to_doc(guild))
        except DuplicateKeyError:
            raise GuildAlreadyExistsError("A guild with this name already exists.")

        doc = await self._collection.find_one({"_id": created.inserted_id})
        return doc_to_guild(doc)

    async def delete(self, guild: Guild) -> None:
        # Validation of ObjectId for delete, if invalid we dont delete
        try:
            oid = ObjectId(guild.id)
        except Exception:
            return None

        await self._collection.delete_one({"_id": oid})

    async def ensure_initialized(self):
        # Ensures guild names are unique 
        await self._collection.create_index("name", unique=True)


# MembershipRepository implementation for MongoDB
class MongoMembershipRepository(MembershipRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["memberships"]

    async def get_user_guilds(self, user_id: str) -> Iterable[GuildMembership]:
        cursor = self._collection.find({"user_id": user_id})
        return [doc_to_membership(doc) async for doc in cursor]

    async def get_membership(self, user_id: str, guild_id: str) -> Optional[GuildMembership]:
        doc = await self._collection.find_one({"user_id": user_id, "guild_id": guild_id})
        if doc is None:
            return None
        return doc_to_membership(doc)

    async def join(self, membership: GuildMembership) -> None:
        await self._collection.insert_one(membership_to_doc(membership))

    async def leave(self, user_id: str, guild_id: str) -> None:
        await self._collection.delete_one({"user_id": user_id, "guild_id": guild_id})

    async def count_members(self, guild_id: str) -> int:
        return await self._collection.count_documents({"guild_id": guild_id})

    async def ensure_initialized(self):
        # Prevent duplicate memberships for same user in same guild, needed for get_membership,leave and join
        await self._collection.create_index(
            [("user_id", 1), ("guild_id", 1)],
            unique=True,
        )

        # Speed up queries for count_members
        await self._collection.create_index("guild_id") 
        # Speed up queries for get_user_guilds
        await self._collection.create_index("user_id")