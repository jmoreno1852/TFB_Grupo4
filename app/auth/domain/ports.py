from abc import ABC, abstractmethod
from typing import Optional

from app.auth.domain.entities import User

#Interface of outbound port for User persistence
class UserRepository(ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Search for user by its email"""
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Search for user by its ID"""
        raise NotImplementedError
    
    @abstractmethod
    async def create(self, user: User) -> User:
        """Create a user in persistence layer of auth domain"""
        raise NotImplementedError
