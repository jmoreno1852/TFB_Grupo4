from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.api.deps import get_current_user
from app.auth.domain.entities import User  
from app.users.api.schemas import UserMeResponse, UpdateProfileRequest, UserSettingsSchema
from app.users.domain.errors import UserNotFoundError, InvalidUpdateError
from app.users.domain.services import UpdateProfileData, UpdateSettingsData
from app.users.dependency_injection.providers import build_users_service

router = APIRouter(prefix="/users", tags=["users"])

#Helper function to return UserMeResponse because of nested schemas and size
def _to_user_me_response(profile) -> UserMeResponse:
    return UserMeResponse(
        user_id=profile.user_id,
        username=profile.username,
        display_name=profile.display_name,
        bio=profile.bio,
        #avatar_url=profile.avatar_url,
        settings=UserSettingsSchema(
            language=profile.settings.language,
            timezone=profile.settings.timezone,
            theme=profile.settings.theme,
        ),
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )

@router.get("/me", response_model=UserMeResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Return current user's profile through user_id from JWT token in get_current_user
    """
    service = build_users_service()

    try:
        profile = await service.get_me(current_user.id)
        return _to_user_me_response(profile)
    except Exception as e:
        #Grabbing exceptions for unexpected errors
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/me", response_model=UserMeResponse)
async def update_me(
    payload: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Partial updates for user profile, protected by JWT getting user_id through get_current_user.
    """
    service = build_users_service()
    #Auxiliar variable for nested settings
    settings_update = None
    if payload.settings is not None:
        settings_update = UpdateSettingsData(
            language=payload.settings.language,
            timezone=payload.settings.timezone,
            theme=payload.settings.theme,
        )

    update_data = UpdateProfileData(
        username=payload.username,
        display_name=payload.display_name,
        bio=payload.bio,
        #avatar_url=payload.avatar_url,
        settings=settings_update,
    )

    try:
        profile = await service.update_me(current_user.id, update_data)
        return _to_user_me_response(profile)

    except UserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except InvalidUpdateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))