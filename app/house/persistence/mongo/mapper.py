from datetime import datetime, timezone
from typing import Any, Dict, List

from app.house.domain.entities import House, HousePlacement


def doc_to_house(doc: Dict[str, Any]) -> House:
    """
    Mongo document to House domain entity.
    """
    placements_docs: List[Dict[str, Any]] = doc.get("placements", [])

    placements = [
        HousePlacement(
            room_index=p["room_index"],
            slot_index=p["slot_index"],
            item_id=p["item_id"],
            placed_at=p.get("placed_at", datetime.now(timezone.utc)),
        )
        for p in placements_docs
    ]

    return House(
        user_id=doc["user_id"],
        placements=placements,
    )


def house_to_doc(house: House) -> Dict[str, Any]:
    """
    House domain entity to Mongo document.
    """
    return {
        "user_id": house.user_id,
        "placements": [
            {
                "room_index": p.room_index,
                "slot_index": p.slot_index,
                "item_id": p.item_id,
                "placed_at": p.placed_at,
            }
            for p in house.placements
        ],
    }