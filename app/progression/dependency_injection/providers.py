from functools import lru_cache

from app.database import get_db

from app.progression.persistence.mongo.repository import MongoProgressionRepository
from app.progression.domain.services import ProgressionService

from app.quests.domain.ports import RewardApplier


@lru_cache(maxsize=1)
def build_progression_repository() -> MongoProgressionRepository:
    """
    Build and return MongoProgressionRepository instance.
    """
    return MongoProgressionRepository(get_db())


@lru_cache(maxsize=1)
def build_progression_service() -> ProgressionService:
    """
    Build and return ProgressionService instanc.
    """
    return ProgressionService(
        progression_repository=build_progression_repository(),
    )


class ProgressionRewardApplier(RewardApplier):
    """
    RewardApplier implementation backed by ProgressionService.
    Used by Quests module to apply XP/Gold rewards without touching persistence directly.
    """

    def __init__(self, progression_service: ProgressionService):
        self.progression_service = progression_service

    async def add_xp(self, user_id: str, amount: int) -> None:
        await self.progression_service.apply_rewards(user_id=user_id, xp=amount, gold=0)

    async def add_gold(self, user_id: str, amount: int) -> None:
        await self.progression_service.apply_rewards(user_id=user_id, xp=0, gold=amount)


@lru_cache(maxsize=1)
def build_reward_applier() -> RewardApplier:
    """
    Build and return RewardApplier instance.
    """
    return ProgressionRewardApplier(
        progression_service=build_progression_service(),
    )


def clear_caches() -> None:
    """
    Clear lru_cache for DI providers.
    Useful in testing when FastAPI TestClient recreates the app multiple times.
    """
    build_reward_applier.cache_clear()
    build_progression_service.cache_clear()
    build_progression_repository.cache_clear()
