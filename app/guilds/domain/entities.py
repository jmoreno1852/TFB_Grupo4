from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

@dataclass(frozen=True)
class Guild:
    """
    Guild entity at domain level
    """
    id: str
    name: str
    description: Optional[str] = None
    type: Optional[str] = None

@dataclass(frozen=True)
class GuildMembership:
    """
    Dataclass representing the relationship user[1]<->guild[1]
    """
    user_id: str
    guild_id: str
    joined_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


