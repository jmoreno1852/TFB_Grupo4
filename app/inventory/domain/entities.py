from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, List


@dataclass(frozen=True)
class Item:
    """
    Represents an item entity in the global catalog of the application.
    """
    id: str
    name: str
    description: Optional[str] = None
    type: str = "misc"  # weapon, armor, furniture, misc, etc.
    equippable_slot: Optional[str] = None  # weapon, armor, etc. (None if not equippable)
    value: int = 0  # Gold value (used by shop)


@dataclass(frozen=True)
class InventoryItem:
    """
    Represents an item owned by a user.
    Stores only item_id reference and quantity.
    """
    item_id: str
    quantity: int = 1


@dataclass(frozen=True)
class Equipment:
    """
    Represents equipped items by slot.
    Each slot stores the item_id or None.
    """
    weapon: Optional[str] = None
    helmet: Optional[str] = None
    armor: Optional[str] = None
    leg_armor: Optional[str] = None
    boots: Optional[str] = None
    accessory: Optional[str] = None


@dataclass(frozen=True)
class Inventory:
    """
    Represents the full inventory of a user.
    Contains owned items and equipped items.
    """
    user_id: str
    items: List[InventoryItem] = field(default_factory=list)
    equipment: Equipment = field(default_factory=Equipment)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None
