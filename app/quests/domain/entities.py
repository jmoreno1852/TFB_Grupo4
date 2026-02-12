from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Literal

#Define possible values for quest status
QuestStatus = Literal["active", "completed"]


@dataclass(frozen=True)
class Quest:
    """
    Quest entity defining quest attributes and metadata at domain layer.
    """
    id: str
    guild_id: str
    title: str
    description: Optional[str] = None
    difficulty: int = 1
    xp_reward: int = 10
    gold_reward: int = 0
    is_active: bool = True
    weight: Optional[int] = None
    cooldown_hours: Optional[int] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


@dataclass(frozen=True)
class UserQuest:
    """
    Quest assigned to user in relationship guild <-> user <-> quest
    """
    user_id: str
    guild_id: str
    quest_id: str
    status: QuestStatus = "active"
    assigned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
