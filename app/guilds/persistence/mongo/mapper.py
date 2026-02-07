from datetime import datetime, timezone
from typing import Any, Dict

from guilds.domain.entities import Guild, GuildMembership


def doc_to_guild(doc: Dict[str, Any]) -> Guild:
    """
    Mongo doc to Guild domain entity.
    """
    return Guild(
        id=str(doc["_id"]),
        name=doc["name"],
        description=doc.get("description"),
        type=doc.get("type"),
    )


def guild_to_doc(guild: Guild) -> Dict[str, Any]:
    """
    Guild domain entity to Mongo document.
    """
    doc: Dict[str, Any] = {
        "name": guild.name,
        "description": guild.description,
    }

    return doc


def doc_to_membership(doc: Dict[str, Any]) -> GuildMembership:
    """
    Mongo doc to GuildMembership domain entity.
    """
    return GuildMembership(
        user_id=doc["user_id"],
        guild_id=doc["guild_id"],
        joined_at=doc.get("joined_at", datetime.now(timezone.utc)),
    )


def membership_to_doc(membership: GuildMembership) -> Dict[str, Any]:
    """
    GuildMembership domain entity to Mongo document.
    """
    return {
        "user_id": membership.user_id,
        "guild_id": membership.guild_id,
        "joined_at": membership.joined_at,
    }
