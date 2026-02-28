from datetime import datetime, timezone
from typing import Any, Dict, cast

from app.quests.domain.entities import Quest, UserQuest


def doc_to_quest(doc: Dict[str, Any]) -> Quest:
    return Quest(
        id=str(doc["_id"]),
        guild_id=doc["guild_id"],
        title=doc["title"],
        description=doc.get("description"),
        difficulty=doc.get("difficulty", 1),
        xp_reward=doc.get("xp_reward", 10),
        gold_reward=doc.get("gold_reward", 0),
        is_active=doc.get("is_active", True),
        weight=doc.get("weight"),
        cooldown_hours=doc.get("cooldown_hours"),
        created_at=doc.get("created_at"),
        updated_at=doc.get("updated_at"),
    )


def quest_to_doc(quest: Quest) -> Dict[str, Any]:
    doc: Dict[str, Any] = {
        "guild_id": quest.guild_id,
        "title": quest.title,
        "description": quest.description,
        "difficulty": quest.difficulty,
        "xp_reward": quest.xp_reward,
        "gold_reward": quest.gold_reward,
        "is_active": quest.is_active,
        "weight": quest.weight,
        "cooldown_hours": quest.cooldown_hours,
        "created_at": quest.created_at,
        "updated_at": quest.updated_at,
    }

    return doc


def doc_to_user_quest(doc: Dict[str, Any]) -> UserQuest:
    assigned_at = cast(datetime | None, doc.get("assigned_at"))
    completed_at = cast(datetime | None, doc.get("completed_at"))

    if assigned_at and assigned_at.tzinfo is None:
        assigned_at = assigned_at.replace(tzinfo=timezone.utc)

    if completed_at and completed_at.tzinfo is None:
        completed_at = completed_at.replace(tzinfo=timezone.utc)

    return UserQuest(
        user_id=doc["user_id"],
        guild_id=doc["guild_id"],
        quest_id=doc["quest_id"],
        status=doc.get("status", "active"),
        assigned_at=doc.get("assigned_at"),
        completed_at=doc.get("completed_at"),
    )


def user_quest_to_doc(user_quest: UserQuest) -> Dict[str, Any]:
    return {
        "user_id": user_quest.user_id,
        "guild_id": user_quest.guild_id,
        "quest_id": user_quest.quest_id,
        "status": user_quest.status,
        "assigned_at": user_quest.assigned_at,
        "completed_at": user_quest.completed_at,
    }
