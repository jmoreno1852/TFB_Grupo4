from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


EquipmentSlot = Literal["weapon", "helmet", "armor", "leg_armor", "boots", "accessory"]


#Inventory Responses
class InventoryItemResponse(BaseModel):
    """
    Entry of an item owned by the user.
    """
    item_id: str
    quantity: int = Field(default=1, ge=1)


class EquipmentResponse(BaseModel):
    """
    Equipped items by slot (stores item_id or None).
    """
    weapon: Optional[str] = None
    helmet: Optional[str] = None
    armor: Optional[str] = None
    leg_armor: Optional[str] = None
    boots: Optional[str] = None
    accessory: Optional[str] = None


class InventoryResponse(BaseModel):
    """
    Full inventory response for a user.
    Includes owned items and equipped items.
    """
    user_id: str
    items: List[InventoryItemResponse]
    equipment: EquipmentResponse
    created_at: datetime
    updated_at: Optional[datetime] = None


#Inventory Requests
class EquipRequest(BaseModel):
    """
    Request to equip an owned item into a given slot.
    """
    item_id: str
    slot: EquipmentSlot


class UnequipRequest(BaseModel):
    """
    Request to unequip item that is currently in the given slot.
    """
    slot: EquipmentSlot


#Catalog Responses
class CatalogItemResponse(BaseModel):
    """
    Item response schema for the global catalog.
    """
    id: str
    name: str
    description: Optional[str] = None
    type: str = "misc"
    equippable_slot: Optional[EquipmentSlot] = None
    value: int = 0


class CatalogListResponse(BaseModel):
    """
    List all items in the global catalog.
    """
    items: List[CatalogItemResponse]