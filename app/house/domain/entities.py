from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List


@dataclass(frozen=True)
class HousePlacement:
    """
    Represents a furniture placement inside a house slot.
    Position is defined by the room_index and slot_index to identify the different instances.
    """
    room_index: int
    slot_index: int
    item_id: str
    placed_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass(frozen=True)
class House:
    """
    House entity related to a user. Contains the distribution of furniture within the different placement slots.
    """
    user_id: str
    placements: List[HousePlacement] = field(default_factory=list)