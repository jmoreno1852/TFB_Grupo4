from typing import Optional

from pydantic import BaseModel, Field


class ShopItemResponse(BaseModel):
    """
    Item response for current shop rotation.
    """
    item_id: str
    name: str
    description: Optional[str] = None
    type: str
    equippable_slot: Optional[str] = None
    value: int  # price comes from catalog Item.value


class PurchaseRequest(BaseModel):
    """
    Purchase request for shop items.
    """
    item_id: str = Field(..., min_length=1)
    quantity: int = Field(default=1, ge=1)


class PurchaseResponse(BaseModel):
    """
    Purchase response.
    """
    status: str = "ok"
    item_id: str
    quantity: int
    total_price: int