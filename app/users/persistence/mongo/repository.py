from typing import Optional

from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from app.users.domain.entities import UserProfile
from app.users.domain.ports import UserProfileRepository
from app.users.persistence.mongo.mapper import doc_to_profile, profile_to_doc, profile_to_update_doc

class MongoUserProfileRepository(UserProfileRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["profiles"]
    
    async def ensure_initialized(self) -> None:
        #Ensure uniq index on user_id
        await self._collection.create_index("user_id", unique=True)
    
    async def get_by_user_id(self, user_id) -> Optional[UserProfile]:
        doc = await self._collection.find_one({"user_id": user_id})
        return doc_to_profile(doc) if doc else None

    async def create(self, profile: UserProfile) -> UserProfile:
        try: 
            res = await self._collection.insert_one(profile_to_doc(profile))
            doc = await self._collection.find_one({"_id": res.inserted_id})
            return doc_to_profile(doc) if doc else None
        except DuplicateKeyError:
            #If exception profile already exists so we can return doc from mongo
            exists = await self._collection.find_one({"user_id": profile.user_id})
            if exists:
                return doc_to_profile(exists)
            raise
    
    async def update(self, user_id: str, profile: UserProfile) -> Optional[UserProfile]:
        update_doc = profile_to_update_doc(profile)
        res = await self._collection.update_one({"user_id": user_id}, update_doc)
        #If profile does not exist return None
        if res.matched_count == 0:
            return None
            
        doc = await self._collection.find_one({"user_id": user_id})
        return doc_to_profile(doc) if doc else None