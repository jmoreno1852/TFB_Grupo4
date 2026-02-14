from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass(frozen=True)
class Stats:
    """
    Base stats for a user progression.
    Increased automatically on level-up.
    """
    strength: int = 0
    focus: int = 0
    resilience: int = 0


@dataclass(frozen=True)
class Progression:
    """
    Represents the progression state of a user.
    Contains level, XP, gold and stats.
    """
    user_id: str
    level: int = 1
    xp: int = 0
    gold: int = 0
    stats: Stats = field(default_factory=Stats)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
