from functools import lru_cache

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.database import get_db
from app.users.domain.services import UsersService
from app.users.persistence.repository import MongoUserProfileRepository


@lru_cache
def build_user_profile_repo() -> MongoUserProfileRepository:
    db: AsyncIOMotorDatabase = get_db()
    repo = MongoUserProfileRepository(db)
    return repo


@lru_cache
def build_users_service() -> UsersService:
    repo = build_user_profile_repo()
    return UsersService(repo)


def clear_users_caches() -> None:
    """
    Clears cached DI singletons for users module, only for testing purposes
    """
    build_users_service.cache_clear()
    build_user_profile_repo.cache_clear()