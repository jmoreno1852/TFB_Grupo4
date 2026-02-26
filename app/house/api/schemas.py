from typing import List

from pydantic import BaseModel, Field


#Responses

class PlacementResponse(BaseModel):
    """
    Single furniture placement response
    """
    room_index: int
    slot_index: int
    item_id: str


class HouseResponse(BaseModel):
    """
    House state response
    """
    user_id: str
    unlocked_rooms: int
    placements: List[PlacementResponse]


#Requests
class PlaceFurnitureRequest(BaseModel):
    """
    Place furniture request
    """
    item_id: str
    room_index: int = Field(..., ge=1, le=5)
    slot_index: int = Field(..., ge=1, le=3)


class RemoveFurnitureRequest(BaseModel):
    """
    Remove furniture request
    """
    room_index: int = Field(..., ge=1, le=5)
    slot_index: int = Field(..., ge=1, le=3)