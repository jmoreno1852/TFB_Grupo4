from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.api.deps import get_current_user
from app.auth.domain.entities import User

from app.shop.api.schemas import ShopItemResponse, PurchaseRequest, PurchaseResponse
from app.shop.domain.errors import ShopItemNotFoundError, CatalogItemNotFoundError
from app.progression.domain.errors import InsufficientGoldError
from app.shop.dependency_injection.providers import build_shop_service

router = APIRouter(prefix="/shop", tags=["shop"])


def _to_shop_item_response(item) -> ShopItemResponse:
    return ShopItemResponse(
        item_id=item.item_id, #Returning item_id so front end can use it to purchase action
        name=item.name,
        description=item.description,
        type=item.type,
        equippable_slot=item.equippable_slot,
        value=item.value,
    )


@router.get("/items", response_model=list[ShopItemResponse])
async def list_shop_items():
    """
    List current shop rotation items.
    """
    service = build_shop_service()

    try:
        items = await service.list_items()
        return [_to_shop_item_response(i) for i in items]

    except CatalogItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/purchase", response_model=PurchaseResponse)
async def purchase_item(payload: PurchaseRequest, current_user: User = Depends(get_current_user)):
    """
    Purchase an item from current shop rotation.
    """
    service = build_shop_service()

    try:
        await service.purchase(
            user_id=current_user.id,
            item_id=payload.item_id,
            quantity=payload.quantity,
        )

        # compute total_price for response catalog value * quantity
        # we reuse list_items to avoid coupling API to catalog gateway.
        items = await service.list_items()
        purchased = next((i for i in items if i.item_id == payload.item_id), None)
        if purchased is None:
            raise ShopItemNotFoundError("Item not found in current shop rotation.")

        return PurchaseResponse(
            status="ok",
            item_id=payload.item_id,
            quantity=payload.quantity,
            total_price=purchased.value * payload.quantity,
        )

    except ShopItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except CatalogItemNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except InsufficientGoldError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))