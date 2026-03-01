from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Iterable, Optional, Protocol

from app.quests.domain.entities import Quest, UserQuest


class QuestCatalogRepository(ABC):
    @abstractmethod
    async def list_active_by_guild(self, guild_id: str) -> Iterable[Quest]:
        """List all active quests for a guild"""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, quest_id: str) -> Optional[Quest]:
        """Get a quest from catalog by its ID"""
        raise NotImplementedError

    @abstractmethod
    async def get_many_by_ids(self, quest_ids: list[str]) -> Iterable[Quest]:
        """Get multiple quests by the IDs, used to merge quest catalog data into user quests response"""
        raise NotImplementedError

    @abstractmethod
    async def create_quest(self, quest: Quest) -> Quest:
        """Create a quest in catalog"""
        raise NotImplementedError

    @abstractmethod
    async def update_quest(self, quest_id: str, updates: dict[str, Any]) -> Optional[Quest]:
        """Update a quest in catalog. Returns updated quest or None if not found"""
        raise NotImplementedError

    @abstractmethod
    async def delete_quest(self, quest_id: str) -> None:
        """Delete a quest from catalog"""
        raise NotImplementedError

    @abstractmethod
    async def ensure_initialized(self) -> None:
        """Ensure that the repository is initialized"""
        raise NotImplementedError

class UserQuestRepository(ABC):
    @abstractmethod
    async def count_active(self, user_id: str, guild_id: str) -> int:
        """Count active assigned quests for a user in a given guild"""
        raise NotImplementedError

    @abstractmethod
    async def list_active_by_user(self, user_id: str) -> Iterable[UserQuest]:
        """List all active quests assigned to the user (includes every guild the user belongs to)"""
        raise NotImplementedError

    @abstractmethod
    async def list_active_by_user_guild(self, user_id: str, guild_id: str) -> Iterable[UserQuest]:
        """List active quests assigned to the user for a specific guild"""
        raise NotImplementedError

    @abstractmethod
    async def list_recent_completed(self, user_id: str, guild_id: str,  limit: int = 10) -> Iterable[UserQuest]:
        """List most recently completed quests for the user in a given guild"""
        raise NotImplementedError

    @abstractmethod
    async def get_active_assignment(self, user_id: str, quest_id: str) -> Optional[UserQuest]:
        """Validation to check if a quest is assigned and active for a user"""
        raise NotImplementedError

    @abstractmethod
    async def get_completed_assignment(self, user_id: str, quest_id: str) -> Optional[UserQuest]:
        """Validation to check if a quest is assigned and completed for a user"""
        raise NotImplementedError

    @abstractmethod
    async def create_assignment(self, user_quest: UserQuest) -> UserQuest:
        """Assign a quest to a user"""
        raise NotImplementedError

    @abstractmethod
    async def mark_completed(self, user_id: str, quest_id: str, completed_at: datetime) -> None:
        """Mark an assigned quest as completed"""
        raise NotImplementedError

    @abstractmethod
    async def ensure_initialized(self) -> None:
        """Ensure that the repository is initialized"""
        raise NotImplementedError

class RewardApplier(ABC):
    @abstractmethod
    async def add_xp(self, user_id: str, amount: int) -> None:
        """Add XP reward to user"""
        raise NotImplementedError

    @abstractmethod
    async def add_gold(self, user_id: str, amount: int) -> None:
        """Add gold reward to user"""
        raise NotImplementedError


class QuestBootstrapper(Protocol):
    async def bootstrap_guild_quests(self, user_id: str, guild_id: str) -> None: 
        """Bootstrap quests for a guild, called when user joins guild for the first time"""
        raise NotImplementedError
