from datetime import datetime, timezone
from typing import Any, Dict, List

from app.inventory.domain.entities import Item, Inventory, InventoryItem, Equipment

#Item mapper
def doc_to_item(doc: Dict[str, Any]) -> Item:
    """
    Mongo doc to Item domain entity.
    Uses Mongo _id as Item.id.
    """
    return Item(
        id=str(doc["_id"]),
        name=doc["name"],
        description=doc.get("description"),
        type=doc.get("type", "misc"),
        equippable_slot=doc.get("equippable_slot"),
        value=int(doc.get("value", 0)),
    )


def item_to_doc(item: Item) -> Dict[str, Any]:
    """
    Item domain entity to Mongo document.
    Uses Item.id as Mongo _id.
    """
    return {
        "_id": item.id,
        "name": item.name,
        "description": item.description,
        "type": item.type,
        "equippable_slot": item.equippable_slot,
        "value": item.value,
    }



#Inventory mapper

def doc_to_inventory(doc: Dict[str, Any]) -> Inventory:
    """
    Mongo doc to Inventory domain entity.
    """
    items_docs: List[Dict[str, Any]] = doc.get("items", [])

    equipment_doc = doc.get("equipment") or {}

    equipment = Equipment(
        weapon=equipment_doc.get("weapon"),
        helmet=equipment_doc.get("helmet"),
        armor=equipment_doc.get("armor"),
        leg_armor=equipment_doc.get("leg_armor"),
        boots=equipment_doc.get("boots"),
        accessory=equipment_doc.get("accessory"),
    )

    inventory_items = [
        InventoryItem(
            item_id=item_doc["item_id"],
            quantity=int(item_doc.get("quantity", 1)),
        )
        for item_doc in items_docs
    ]

    return Inventory(
        user_id=doc["user_id"],
        items=inventory_items,
        equipment=equipment,
        created_at=doc.get("created_at", datetime.now(timezone.utc)),
        updated_at=doc.get("updated_at"),
    )


def inventory_to_doc(inventory: Inventory) -> Dict[str, Any]:
    """
    Inventory domain entity to Mongo document.
    """
    return {
        "user_id": inventory.user_id,
        "items": [
            {
                "item_id": item.item_id,
                "quantity": item.quantity,
            }
            for item in inventory.items
        ],
        "equipment": {
            "weapon": inventory.equipment.weapon,
            "helmet": inventory.equipment.helmet,
            "armor": inventory.equipment.armor,
            "leg_armor": inventory.equipment.leg_armor,
            "boots": inventory.equipment.boots,
            "accessory": inventory.equipment.accessory,
        },
        "created_at": inventory.created_at,
        "updated_at": inventory.updated_at,
    }
