from functools import lru_cache

from app.database import get_db

from app.quests.domain.services import QuestsService
from app.quests.persistence.mongo.repository import QuestCatalogMongoRepository, UserQuestMongoRepository

#Import RewardApplier from progression module
from app.progression.dependency_injection.providers import build_reward_applier as build_progression_reward_applier



@lru_cache(maxsize=1)
def build_quest_catalog_repository() -> QuestCatalogMongoRepository:
    """
    Build and return QuestCatalogMongoRepository instance.
    """
    return QuestCatalogMongoRepository(get_db())


@lru_cache(maxsize=1)
def build_user_quest_repository() -> UserQuestMongoRepository:
    """
    Build and return UserQuestMongoRepository instance.
    """
    return UserQuestMongoRepository(get_db())


def build_reward_applier(): 
    """
    Build and return RewardApplier implementation.
    """
    return build_progression_reward_applier()


@lru_cache(maxsize=1)
def build_quests_service() -> QuestsService:
    """
    Build and return QuestsService instance.
    """
    return QuestsService(
        quest_catalog_repository=build_quest_catalog_repository(),
        user_quest_repository=build_user_quest_repository(),
        reward_applier=build_reward_applier(),
        active_quests_per_guild=3,
        recent_completed_limit=10,
    )


def clear_caches() -> None:
    """
    Clear lru_cache for DI providers.
    Useful in testing when FastAPI TestClient recreates the app multiple times.
    """
    build_quests_service.cache_clear()
    build_quest_catalog_repository.cache_clear()
    build_user_quest_repository.cache_clear()
