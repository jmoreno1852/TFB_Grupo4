from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.house.domain.entities import House, HousePlacement
from app.house.domain.errors import (
    HouseLockedError,
    RoomLockedError,
    InvalidPlacementError,
    ItemNotOwnedError,
    InvalidItemTypeError,
    FurnitureNotFoundError,
)
from app.house.domain.ports import HouseRepository, InventoryGateway, ProgressionGateway


class HouseService:
    def __init__(
        self,
        house_repository: HouseRepository,
        inventory_gateway: InventoryGateway,
        progression_gateway: ProgressionGateway,
    ):
        self.house_repository = house_repository
        self.inventory_gateway = inventory_gateway
        self.progression_gateway = progression_gateway

    async def get_house(self, user_id: str) -> Dict:
        user_id_norm = user_id.strip()

        house = await self._get_or_create_house(user_id_norm)
        unlocked_rooms = await self._get_unlocked_rooms(user_id_norm)

        return {
            "user_id": house.user_id,
            "unlocked_rooms": unlocked_rooms,
            "placements": [
                {"room_index": p.room_index, "slot_index": p.slot_index, "item_id": p.item_id}
                for p in house.placements
            ],
        }

    async def place_furniture(self, user_id: str, item_id: str, room_index: int, slot_index: int) -> Dict:
        user_id_norm = user_id.strip()
        item_id_norm = item_id.strip()

        self._validate_position(room_index, slot_index)

        unlocked_rooms = await self._get_unlocked_rooms(user_id_norm)
        self._enforce_room_unlocked(unlocked_rooms, room_index)

        owned_item = await self.inventory_gateway.get_user_item(user_id_norm, item_id_norm)
        if owned_item is None:
            raise ItemNotOwnedError("User does not own the specified item.")

        if owned_item.get("type") != "furniture":
            raise InvalidItemTypeError("Only items of type 'furniture' can be placed.")

        house = await self._get_or_create_house(user_id_norm)
        # Check if slot already occupied to return previous item to inventory
        replaced_item_id: str | None = None
        for p in house.placements:
            if p.room_index == room_index and p.slot_index == slot_index:
                replaced_item_id = p.item_id
                break
        
        # Decrease item quantity from inventory 
        await self.inventory_gateway.consume_item(user_id_norm, item_id_norm, amount=1)

        # If there was a replaced item, return it to the user's inventory
        if replaced_item_id is not None:
            await self.inventory_gateway.grant_item(user_id_norm, replaced_item_id, amount=1)

        # Replace placement if slot already occupied
        new_placement = HousePlacement(
            room_index=room_index,
            slot_index=slot_index,
            item_id=item_id_norm,
            placed_at=datetime.now(timezone.utc),
        )
        #Create new placement list without the replaced one
        new_placements: List[HousePlacement] = [
            p for p in house.placements
            if not (p.room_index == room_index and p.slot_index == slot_index)
        ]
        #We append the new placement
        new_placements.append(new_placement)

        updated_house = replace(house, placements=new_placements)
        await self.house_repository.save(updated_house)

        return {
            "user_id": updated_house.user_id,
            "unlocked_rooms": unlocked_rooms,
            "placements": [
                {"room_index": p.room_index, "slot_index": p.slot_index, "item_id": p.item_id}
                for p in updated_house.placements
            ],
        }

    async def remove_furniture(self, user_id: str, room_index: int, slot_index: int) -> Dict:
        user_id_norm = user_id.strip()

        self._validate_position(room_index, slot_index)

        unlocked_rooms = await self._get_unlocked_rooms(user_id_norm)
        self._enforce_room_unlocked(unlocked_rooms, room_index)

        house = await self._get_or_create_house(user_id_norm)

        # Check if there is furniture in the specified slot
        removed_item_id: str | None = None
        for p in house.placements:
            if p.room_index == room_index and p.slot_index == slot_index:
                removed_item_id = p.item_id
                break

        if removed_item_id is None:
            raise FurnitureNotFoundError("No furniture found in the specified slot.")

        # Return the item to the user's inventory
        await self.inventory_gateway.grant_item(user_id_norm, removed_item_id, amount=1)
        
        new_placements = [
            p for p in house.placements
            if not (p.room_index == room_index and p.slot_index == slot_index)
        ]

        updated_house = replace(house, placements=new_placements)
        await self.house_repository.save(updated_house)

        return {
            "user_id": updated_house.user_id,
            "unlocked_rooms": unlocked_rooms,
            "placements": [
                {"room_index": p.room_index, "slot_index": p.slot_index, "item_id": p.item_id}
                for p in updated_house.placements
            ],
        }
    
    #Defining internal functions as they are usually called for checks
    async def _get_or_create_house(self, user_id: str) -> House:
        house = await self.house_repository.get_by_user(user_id)
        if house is None:
            house = House(user_id=user_id, placements=[])
            await self.house_repository.save(house)
        return house

    async def _get_unlocked_rooms(self, user_id: str) -> int:

        level = await self.progression_gateway.get_level(user_id)
        unlocked = level // 5
        if unlocked > 5:
            unlocked = 5
        if unlocked < 0:
            unlocked = 0
        return unlocked

    def _validate_position(self, room_index: int, slot_index: int) -> None:
        if room_index < 1 or room_index > 5 or slot_index < 1 or slot_index > 3:
            raise InvalidPlacementError("Invalid (room_index, slot_index).")

    def _enforce_room_unlocked(self, unlocked_rooms: int, room_index: int) -> None:
        if unlocked_rooms <= 0:
            raise HouseLockedError("User has no unlocked rooms yet.")
        if room_index > unlocked_rooms:
            raise RoomLockedError("Room is locked for current user level.")