from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class UserSettings:
    """
    User settings to store user preferences
    This can be extended after MVP
    """
    language: str = "en"
    timezone: str = "UTC"
    theme: str = "light" # This value could be extended in the future if more themes are added

@dataclass(frozen=True)
class UserProfile:
    """
    User profile entity to store user information
    """
    #Connects with value of User entity in the auth module
    user_id: str
    username: str
    display_name: str
    bio: Optional[str] = None
    #avatar_url: Optional[str] = None # Future implementation for user avatars
    #Using this format to avoid mutable default argument issues between instances
    settings: UserSettings = field(default_factory=UserSettings) 
    created_at: datetime = field(default_factory=datetime.timezone.utcnow)
    updated_at: datetime = field(default_factory=datetime.timezone.utcnow)



