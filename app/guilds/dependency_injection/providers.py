from functools import lru_cache

from app.database import get_db

from app.guilds.persistence.mongo.repository import (
    MongoGuildRepository,
    MongoMembershipRepository,
)
from app.guilds.domain.services import GuildsService
#Import for QuestBootstrapper protocol
from app.quests.dependency_injection.providers import build_quest_bootstrapper


@lru_cache(maxsize=1)
def build_guild_repository() -> MongoGuildRepository:
    """
    Build and return MongoGuildRepository instance, using lru_cache to ensure singleton behavior.
    """
    return MongoGuildRepository(get_db())


@lru_cache(maxsize=1)
def build_membership_repository() -> MongoMembershipRepository:
    """
    Build and return MongoMembershipRepository instance, using lru_cache to ensure singleton behavior.
    """
    return MongoMembershipRepository(get_db())


@lru_cache(maxsize=1)
def build_guilds_service() -> GuildsService:
    """
    Build and return GuildsService instance, using lru_cache to ensure singleton behavior.
    """
    return GuildsService(
        guild_repository=build_guild_repository(),
        membership_repository=build_membership_repository(),
        quest_bootstrapper=build_quest_bootstrapper(),
    )


def clear_caches() -> None:
    """
    Clear lru_cache for DI providers.
    Useful in testing when FastAPI TestClient recreates the app multiple times.
    """
    build_guilds_service.cache_clear()
    build_guild_repository.cache_clear()
    build_membership_repository.cache_clear()
