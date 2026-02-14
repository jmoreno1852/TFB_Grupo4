from abc import ABC, abstractmethod

from progression.domain.entities import Progression


class ProgressionRepository(ABC):
    """
    Outbound port for Progression persistence.
    Handles user progression state (XP, level, gold, stats).
    """

    @abstractmethod
    async def get_by_user(self, user_id: str) -> Progression:
        """
        Retrieve progression for a user.
        Implementation with lazy initialization, returns default progression if not found as in /app/users module.
        """
        raise NotImplementedError

    @abstractmethod
    async def update_progression(self, progression: Progression) -> None:
        """
        Updates progression in persistence layer.
        """
        raise NotImplementedError

    @abstractmethod
    async def spend_gold(self, user_id: str, amount: int) -> Progression:
        """
        Decrease gold from user progression.
        """
        raise NotImplementedError
