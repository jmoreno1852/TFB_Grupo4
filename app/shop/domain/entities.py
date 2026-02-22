from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class ShopListing:
    """
    Item currently available in the shop rotation. Stores the item_id reference and availability window of the item.
    """
    item_id: str
    available_from: datetime
    available_to: datetime


@dataclass(frozen=True)
class ShopItemView:
    """
    Class to show item information in Shop endpoint.
    """
    item_id: str
    name: str
    description: Optional[str] = None
    type: str = "misc"  # weapon, armor, furniture, misc, etc.
    equippable_slot: Optional[str] = None  # weapon, armor, etc. (None if not equippable)
    value: int = 0  