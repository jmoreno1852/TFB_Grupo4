#Typing imports
from typing import Optional
#DB functionality imports
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
#Domain imports
from app.auth.domain.entities import User
from app.auth.domain.ports import UserRepository
from app.auth.domain.errors import UserAlreadyExistsError
from app.auth.persistence.mongo.mapper import user_to_db, db_to_user


#Define the functionality of the Repositories for this Domain
#UserRepository implementation for MongoDB
class MongoUserRepository(UserRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        self._collection = db["users"]
    
    #Implementation of get_by_email for MongoDB
    async def get_by_email(self, email: str) -> Optional[User]:
        doc = await self._collection.find_one({"email": email})
        if doc is None:
            return None
        return db_to_user(doc)

    #Implementation of get_by_id for MongoDB
    async def get_by_id(self, user_id: str) -> Optional[User]:
        #Validate if the string in user_id is a valid ObjectId
        try:
            oid = ObjectId(user_id)
        except Exception:
            return None
        doc = await self._collection.find_one({"_id": oid})
        if doc is None:
            return None
        return db_to_user(doc)
    
    #Implementation of create for MongoDB
    async def create(self, user: User) -> User:
        #Check if email is unique in MongoDB
        try:
            create_user = await self._collection.insert_one(user_to_db(user)) 
        except DuplicateKeyError:
            raise UserAlreadyExistsError("An account related to this email already exists.")
        doc = await self._collection.find_one({"_id": create_user.inserted_id})
        return db_to_user(doc)
    
    #Ensure index and uniqueness of the value email in MongoDB collection
    async def ensure_initialized(self):
        await self._collection.create_index("email", unique=True)