from datetime import datetime
from typing import Any, Dict

from app.users.domain.entities import UserProfile, UserSettings


def doc_to_profile(doc: Dict[str, Any]) -> UserProfile:
    """
    Mongo doc to UserProfile domain entity.
    """
    return UserProfile(
        user_id=doc["user_id"],
        username=doc["username"],
        display_name=doc["display_name"],
        bio=doc.get("bio"),
        #avatar_url=doc.get("avatar_url"),
        settings=UserSettings(
            language=doc.get("settings", {}).get("language", "es"),
            timezone=doc.get("settings", {}).get("timezone", "Europe/Madrid"),
            theme=doc.get("settings", {}).get("theme", "dark"),
        ),
        created_at=doc.get("created_at", datetime.now(datetime.timezone.utc)),
        updated_at=doc.get("updated_at", datetime.now(datetime.timezone.utc)),
    )


def profile_to_doc(profile: UserProfile) -> Dict[str, Any]:
    """
    UserProfile domain entity to Mongo document.
    """
    return {
        "user_id": profile.user_id,
        "username": profile.username,
        "display_name": profile.display_name,
        "bio": profile.bio,
        #"avatar_url": profile.avatar_url,
        "settings": {
            "language": profile.settings.language,
            "timezone": profile.settings.timezone,
            "theme": profile.settings.theme,
        },
        "created_at": profile.created_at,
        "updated_at": profile.updated_at,
    }


def profile_to_update_doc(profile: UserProfile) -> Dict[str, Any]:
    """
    UserProfile to Mongo update document. This implementation uses $set to change mutable fields in the document.
    """
    return {
        "$set": {
            "username": profile.username,
            "display_name": profile.display_name,
            "bio": profile.bio,
            # "avatar_url": profile.avatar_url,
            "settings": {
                "language": profile.settings.language,
                "timezone": profile.settings.timezone,
                "theme": profile.settings.theme,
            },
            "updated_at": profile.updated_at,
        }
    }