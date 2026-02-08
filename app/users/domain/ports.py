from abc import ABC, abstractmethod
from typing import Optional

from app.users.domain.entities import UserProfile

class UserProfileRepository(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> Optional[UserProfile]:
        """Search for profile by its user_id"""
        raise NotImplementedError
    #Create defined as we are implementing a lazy initialization where user is created in auth
    #The profile is created when user first GET its profile
    @abstractmethod
    async def create(self, user_profile: UserProfile) -> UserProfile:
        """Create a user profile in persistence layer of users domain"""
        raise NotImplementedError
    @abstractmethod
    async def update(self, user_id: str, profile: UserProfile) -> Optional[UserProfile]:
        """Update user profile in persistence layer of users domain"""
        raise NotImplementedError