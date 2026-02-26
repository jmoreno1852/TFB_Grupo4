from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.api.deps import get_current_user
from app.auth.domain.entities import User

from app.house.api.schemas import (
    HouseResponse,
    PlaceFurnitureRequest,
    RemoveFurnitureRequest,
)
from app.house.domain.errors import (
    HouseLockedError,
    RoomLockedError,
    InvalidPlacementError,
    ItemNotOwnedError,
    InvalidItemTypeError,
)
from app.house.dependency_injection.providers import build_house_service


router = APIRouter(prefix="/house", tags=["house"])


def _to_house_response(data) -> HouseResponse:
    return HouseResponse(
        user_id=data["user_id"],
        unlocked_rooms=data["unlocked_rooms"],
        placements=data["placements"],
    )


@router.get("/me", response_model=HouseResponse)
async def get_my_house(current_user: User = Depends(get_current_user)):
    """
    Get current user's house.
    """
    service = build_house_service()

    try:
        data = await service.get_house(user_id=current_user.id)
        return _to_house_response(data)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/place", response_model=HouseResponse)
async def place_furniture(payload: PlaceFurnitureRequest, current_user: User = Depends(get_current_user)):
    """
    Place furniture in a room slot.
    """
    service = build_house_service()

    try:
        data = await service.place_furniture(
            user_id=current_user.id,
            item_id=payload.item_id,
            room_index=payload.room_index,
            slot_index=payload.slot_index,
        )
        return _to_house_response(data)

    except (HouseLockedError, RoomLockedError) as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except InvalidPlacementError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except ItemNotOwnedError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except InvalidItemTypeError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/remove", response_model=HouseResponse)
async def remove_furniture(payload: RemoveFurnitureRequest, current_user: User = Depends(get_current_user)):
    """
    Remove furniture from a room slot.
    """
    service = build_house_service()

    try:
        data = await service.remove_furniture(
            user_id=current_user.id,
            room_index=payload.room_index,
            slot_index=payload.slot_index,
        )
        return _to_house_response(data)

    except (HouseLockedError, RoomLockedError) as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))

    except InvalidPlacementError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))