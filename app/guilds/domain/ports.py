from abc import ABC, abstractmethod
from typing import Iterable, Optional

from app.guilds.domain.entities import Guild, GuildMembership


class GuildRepository(ABC):
    @abstractmethod
    async def list_all(self) -> Iterable[Guild]:
        """List all available guilds as a catalog"""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, guild_id: str) -> Optional[Guild]:
        """Search for a guild by its ID"""
        raise NotImplementedError

    @abstractmethod
    async def create(self, guild: Guild) -> Guild:
        """Create a guild in persistence layer"""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, guild: Guild) -> None:
        """Delete a guild in persistence layer"""
        raise NotImplementedError

    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[Guild]:
        """Search for a guild by its name"""
        raise NotImplementedError

    @abstractmethod
    async def ensure_initialized(self) -> None:
        """Ensure that the repository is initialized"""
        raise NotImplementedError

# Interface of outbound port for Membership persistence
class MembershipRepository(ABC):
    @abstractmethod
    async def get_user_guilds(self, user_id: str) -> Iterable[GuildMembership]:
        """List all guild memberships for given user"""
        raise NotImplementedError

    @abstractmethod
    async def get_membership(self, user_id: str, guild_id: str) -> Optional[GuildMembership]:
        """Get specific membership (user <-> guild)"""
        raise NotImplementedError

    @abstractmethod
    async def join(self, membership: GuildMembership) -> None:
        """Create new guild membership"""
        raise NotImplementedError
    
    @abstractmethod
    async def leave(self, user_id: str, guild_id: str) -> None:
        """Remove user from a guild"""
        raise NotImplementedError
    
    @abstractmethod
    async def count_members(self, guild_id: str) -> int:
        """Check ammount of members in a guild"""
        raise NotImplementedError

    @abstractmethod
    async def ensure_initialized(self) -> None:
        """Ensure that the repository is initialized"""
        raise NotImplementedError