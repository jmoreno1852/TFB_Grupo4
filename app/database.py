#Import async client for MongoDB
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
#Import settings from config.py
from app.config import settings
#Import timezone for tz-aware datetime
from datetime import timezone
#Global variables
_client: AsyncIOMotorClient | None = None
_db: AsyncIOMotorDatabase | None = None

#Function to get MongoDB Client
def get_client() -> AsyncIOMotorClient:
    global _client
    if _client is None:
        _client = AsyncIOMotorClient(settings.MONGO_URI, tz_aware=True, tzinfo=timezone.utc)
    return _client

#Function to get MongoDB Database
def get_db() -> AsyncIOMotorDatabase:
    global _db
    if _db is None:
        client = get_client()
        _db = client[settings.MONGO_DB_NAME]
    return _db

#Function to close connection to MongoDB
async def close_db():
    global _client,_db
    if _client is not None:
        _client.close()
    _client = None
    _db = None