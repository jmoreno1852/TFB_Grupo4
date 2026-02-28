from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.api.deps import get_current_user
from app.auth.domain.entities import User

from app.guilds.api.schemas import (
    GuildResponse,
    ListGuildsResponse,
    JoinGuildRequest,
    CreateGuildRequest,
    CreateGuildResponse,
    DeleteGuildResponse,
)
from app.guilds.domain.errors import (
    GuildNotFoundError,
    AlreadyInGuildError,
    NotInGuildError,
    GuildAlreadyExistsError,
    InvalidGuildNameError,
    GuildHasMembersError,
)
from app.guilds.dependency_injection.providers import build_guilds_service
from app.guilds.domain.services import GuildsService

router = APIRouter(prefix="/guilds", tags=["guilds"])


def _to_guild_response(guild) -> GuildResponse:
    return GuildResponse(
        id=guild.id,
        name=guild.name,
        description=guild.description,
    )


@router.get("", response_model=ListGuildsResponse)
async def list_guilds(service: GuildsService = Depends(build_guilds_service)):
    """
    List all available guilds (catalog).
    """
    try:
        guilds = await service.list_guilds()
        return ListGuildsResponse(guilds=[_to_guild_response(g) for g in guilds])
    except Exception as e:
        #Detail=str should not be used in production 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("", response_model=CreateGuildResponse, status_code=status.HTTP_201_CREATED)
async def create_guild(payload: CreateGuildRequest, service: GuildsService = Depends(build_guilds_service)):
    """
    Create a new guild.
    """

    try:
        guild = await service.create_guild(name=payload.name, description=payload.description)
        return CreateGuildResponse(guild=_to_guild_response(guild))

    except GuildAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    except InvalidGuildNameError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{guild_id}", response_model=DeleteGuildResponse)
async def delete_guild(guild_id: str, service: GuildsService = Depends(build_guilds_service)):
    """
    Delete a guild. Only guilds with no active membershipts can be deleted.
    """
    try:
        await service.delete_guild(guild_id)
        return DeleteGuildResponse(deleted=True)

    except GuildNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except GuildHasMembersError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.post("/join", status_code=status.HTTP_204_NO_CONTENT)
async def join_guild(payload: JoinGuildRequest, current_user: User = Depends(get_current_user), service: GuildsService = Depends(build_guilds_service)):
    """
    Join a guild.
    """
    try:
        await service.join_guild(user_id=current_user.id, guild_id=payload.guild_id)
        return

    except GuildNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except AlreadyInGuildError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/leave", status_code=status.HTTP_204_NO_CONTENT)
async def leave_guild(payload: JoinGuildRequest, current_user: User = Depends(get_current_user), service: GuildsService = Depends(build_guilds_service)):
    """
    Leave a guild.
    """
    try:
        await service.leave_guild(user_id=current_user.id, guild_id=payload.guild_id)
        return

    except NotInGuildError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))





