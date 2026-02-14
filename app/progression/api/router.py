from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.api.deps import get_current_user
from app.auth.domain.entities import User

from app.progression.api.schemas import (
    StatsResponse,
    ProgressResponse,
    GetProgressResponse,
)
from app.progression.dependency_injection.providers import build_progression_service


router = APIRouter(prefix="/progression", tags=["progression"])


def _to_progress_response(prog) -> ProgressResponse:
    return ProgressResponse(
        user_id=prog.user_id,
        level=prog.level,
        xp=prog.xp,
        gold=prog.gold,
        stats=StatsResponse(
            strength=prog.stats.strength,
            focus=prog.stats.focus,
            resilience=prog.stats.resilience,
        ),
        created_at=prog.created_at.isoformat(),
        updated_at=prog.updated_at.isoformat() if prog.updated_at else None,
    )


@router.get("/me", response_model=GetProgressResponse)
async def get_my_progress(current_user: User = Depends(get_current_user)):
    """
    Get current user progression (lazy init if missing).
    """
    service = build_progression_service()

    try:
        prog = await service.get_progress(current_user.id)
        return GetProgressResponse(progression=_to_progress_response(prog))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
