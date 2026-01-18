from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from app.users.domain.entities import UserProfile, UserSettings
from app.users.domain.ports import UserProfileRepository
from app.users.domain.errors import UserNotFoundError, InvalidUpdateError


@dataclass(frozen=True)
class UpdateSettingsData:
    language: Optional[str] = None
    timezone: Optional[str] = None
    theme: Optional[str] = None

@dataclass(frozen=True)
class UpdateProfileData:
    """
    Domain level update command.
    All fields are defined as optional so we can do partials updates.
    """
    #We do not define user_id and username as they should not be updated
    display_name: Optional[str] = None
    bio: Optional[str] = None
    #avatar_url: Optional[str] = None # Future implementation for user avatars
    #Nesting settings into Profile update as settings will be part of the profile. 
    #We will have only one endpoint to patch depending on the json received by the user we will update settings or profile fields
    settings: Optional[UpdateSettingsData] = None

class UsersService:
    def __init__(self, repo: UserProfileRepository):
        self.repo = repo
    
    async def get_me(self, user_id: str) -> UserProfile:
        """
        If profile exists for specified user_id, return it.
        If not, create a profile and return it.
        """ 
        profile = await self.repo.get_by_user_id(user_id)
        if profile is not None:
            return profile
        
        #Default values for new profile, in the future we can prompt the user at first login
        #That prompt loads the profile for the lazy initializatio, we ask for username, display_name...
        #user_id will be longer that 6 characters as it is the ObjectId from MongoDB, but contemplating the case it is not
        #Also user_id[-6:] could create collisions but for default values it is acceptable
        default_username = f"user_{user_id[-6:]}" if len(user_id) >= 6 else f"user_{user_id}"

        default_profile = UserProfile(
            user_id = user_id,
            username = default_username,
            display_name= default_username,
            bio = None,
            settings = UserSettings(
                language="en",
                timezone="UTC",
                theme="light"
            ),
            created_at = datetime.now(timezone.utc),
            updated_at = datetime.now(timezone.utc),
            #avatar_url =none,
        )

        created = await self.repo.create(default_profile)
        return created

    async def update_me(self, user_id: str, data: UpdateProfileData) -> UserProfile:
        """
        Update data for current user's profile and settings.
        """
        profile = await self.repo.get_by_user_id(user_id)
        if profile is None:
            raise UserNotFoundError("User profile not found.")
        
        #Basic validaton of data at domain level
        #Username validation
        if data.username is not None:
            username = data.username.strip()
            if not username:
                raise InvalidUpdateError("Username can not be empty.")
            if len(username) < 3 or len(username) > 30:
                raise InvalidUpdateError("Username must be between 3 and 30 characters long.")
        else:
            username = profile.username
        #Display name validation
        if data.display_name is not None:
            display_name = data.display_name.strip()
            if not display_name:
                raise InvalidUpdateError("Display name can not be empty.")
            if len(display_name) > 40:
                raise InvalidUpdateError("Display name too long, maximum 40 characters.")
        else:
            display_name = profile.display_name
        
        #Biografy validation
        # Optional fields: allow empty bio -> normalize to None
        bio = data.bio.strip() if data.bio is not None else profile.bio
        if bio == "":
            bio = None
        if bio is not None and len(bio) > 280:
            raise InvalidUpdateError("bio too long (max 280 chars)")

        # Avatar URL validation - Future implementation
        #avatar_url = data.avatar_url.strip() if data.avatar_url is not None else profile.avatar_url
        #if avatar_url == "":
        #    avatar_url = None
        #if avatar_url is not None and len(avatar_url) > 2048:
        #    raise InvalidUpdateError("avatar_url too long")

        # Settings update validation, optional and nested
        new_settings = profile.settings
        if data.settings is not None:
            lang = data.settings.language.strip() if data.settings.language is not None else profile.settings.language
            tz = data.settings.timezone.strip() if data.settings.timezone is not None else profile.settings.timezone
            th = data.settings.theme.strip() if data.settings.theme is not None else profile.settings.theme

            if not lang:
                raise InvalidUpdateError("language cannot be empty")
            if not tz:
                raise InvalidUpdateError("timezone cannot be empty")
            if not th:
                raise InvalidUpdateError("theme cannot be empty")

            new_settings = UserSettings(
                language=lang,
                timezone=tz,
                theme=th,
            )

        updated = UserProfile(
            user_id=profile.user_id,
            username=username,
            display_name=display_name,
            bio=bio,
            #avatar_url=avatar_url,
            settings=new_settings,
            created_at=profile.created_at,
            updated_at=datetime.now(timezone.utc),
        )

        saved_update = await self.repo.update(user_id=user_id, profile=updated)
        if saved_update is None:
            # Race condition check, should not happen normally
            raise UserNotFoundError("Profile not found")

        return saved_update


        
