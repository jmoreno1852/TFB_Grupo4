
from functools import lru_cache

from app.database import get_db
from app.auth.persistence.mongo.repository import MongoUserRepository
from app.auth.domain.services import AuthService
from app.auth.domain.ports import UserRepository

@lru_cache(maxsize=1)
def build_user_repo() -> UserRepository:
    """Build and return MongoUserRepository instance, using lru_cache to ensure singleton behavior."""
    repo = MongoUserRepository(get_db())
    return repo


@lru_cache(maxsize=1)
def build_auth_service() -> AuthService:
    """Build and return AuthService instance, using lru_cache to ensure singleton behavior."""
    return AuthService(build_user_repo())

def clear_caches() -> None:
    """Clear lru_cache for DI providers, useful only in testing when instance of app is recreated multiple times.
    In case testing is needed through pytest and FastAPI's TestClient. As TestClient creates new app instance per test module.
    """
    build_auth_service.cache_clear()
    build_user_repo.cache_clear()
