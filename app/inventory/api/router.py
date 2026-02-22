from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.api.deps import get_current_user
from app.auth.domain.entities import User

from app.inventory.api.schemas import (
    InventoryResponse,
    EquipRequest,
    UnequipRequest,
    CatalogItemResponse,
    CatalogListResponse,
)
from app.inventory.domain.errors import (
    ItemNotOwnedError,
    SlotInvalidError,
    ItemNotFoundInCatalogError,
    ItemNotEquippableError,
)
from app.inventory.dependency_injection.providers import (
    build_inventory_service,
    build_catalog_service,
)


router = APIRouter(prefix="/inventory", tags=["inventory"])


def _to_inventory_response(inv) -> InventoryResponse:
    return InventoryResponse(
        user_id=inv.user_id,
        items=[{"item_id": i.item_id, "quantity": i.quantity} for i in inv.items],
        equipment={
            "weapon": inv.equipment.weapon,
            "helmet": inv.equipment.helmet,
            "armor": inv.equipment.armor,
            "leg_armor": inv.equipment.leg_armor,
            "boots": inv.equipment.boots,
            "accessory": inv.equipment.accessory,
        },
        created_at=inv.created_at,
        updated_at=inv.updated_at,
    )


def _to_catalog_item_response(item) -> CatalogItemResponse:
    return CatalogItemResponse(
        id=item.id,
        name=item.name,
        description=item.description,
        type=item.type,
        equippable_slot=item.equippable_slot,
        value=item.value,
    )


@router.get("/me", response_model=InventoryResponse)
async def get_my_inventory(current_user: User = Depends(get_current_user)):
    """
    Get current user's inventory including equipment.
    """
    service = build_inventory_service()

    try:
        inventory = await service.get_inventory(user_id=current_user.id)
        return _to_inventory_response(inventory)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/equip", response_model=InventoryResponse)
async def equip_item(payload: EquipRequest, current_user: User = Depends(get_current_user)):
    """
    Equip an owned item into a slot.
    """
    service = build_inventory_service()

    try:
        inventory = await service.equip_item(
            user_id=current_user.id,
            item_id=payload.item_id,
            slot=payload.slot,
        )
        return _to_inventory_response(inventory)

    except SlotInvalidError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except ItemNotOwnedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    except ItemNotFoundInCatalogError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except ItemNotEquippableError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/unequip", response_model=InventoryResponse)
async def unequip_item(payload: UnequipRequest, current_user: User = Depends(get_current_user)):
    """
    Unequip whatever is currently in the given slot.
    """
    service = build_inventory_service()

    try:
        inventory = await service.unequip_item(
            user_id=current_user.id,
            slot=payload.slot,
        )
        return _to_inventory_response(inventory)

    except SlotInvalidError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/catalog", response_model=CatalogListResponse)
async def list_catalog_items():
    """
    List all available items in the global catalog.
    """
    service = build_catalog_service()

    try:
        items = await service.list_catalog_items()
        return CatalogListResponse(items=[_to_catalog_item_response(i) for i in items])

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/catalog/{item_id}", response_model=CatalogItemResponse)
async def get_catalog_item(item_id: str):
    """
    Get a specific catalog item by id.
    """
    service = build_catalog_service()

    try:
        item = await service.get_catalog_item(item_id=item_id)
        return _to_catalog_item_response(item)

    except ItemNotFoundInCatalogError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))