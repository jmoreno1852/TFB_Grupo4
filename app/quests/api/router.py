from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.api.deps import get_current_user
from app.auth.domain.entities import User

from app.quests.api.schemas import (
    QuestResponse,
    ListUserQuestsResponse,
    CompleteQuestResponse,
    BootstrapGuildQuestsResponse,
    CreateQuestRequest,
    UpdateQuestRequest,
    DeleteQuestResponse,
)
from app.quests.domain.errors import (
    QuestNotFoundError,
    QuestAlreadyCompletedError,
    QuestNotAssignedError,
    QuestUpdateError,
    QuestDeleteError,
)
from app.quests.dependency_injection.providers import build_quests_service


router = APIRouter(prefix="/quests", tags=["quests"])


def _to_quest_response(quest, assignment) -> QuestResponse:
    return QuestResponse(
        id=quest.id,
        guild_id=quest.guild_id,
        title=quest.title,
        description=quest.description,
        difficulty=quest.difficulty,
        xp_reward=quest.xp_reward,
        gold_reward=quest.gold_reward,
        is_active=quest.is_active,
        weight=quest.weight,
        cooldown_hours=quest.cooldown_hours,
        status=assignment.status,
        assigned_at=assignment.assigned_at,
        completed_at=assignment.completed_at,
    )


@router.get("", response_model=ListUserQuestsResponse)
async def list_user_quests(current_user: User = Depends(get_current_user)):
    """
    List active quests assigned to current user.
    """
    service = build_quests_service()

    try:
        merged = await service.list_user_quests(current_user.id)
        quests = [_to_quest_response(m["quest"], m["assignment"]) for m in merged]
        return ListUserQuestsResponse(quests=quests)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/{quest_id}/complete", response_model=CompleteQuestResponse)
async def complete_quest(quest_id: str, current_user: User = Depends(get_current_user)):
    """
    Complete an active quest assigned to the current user.
    Marks quest as completed, applies rewards and assigns a new quest for the same guild.
    """
    service = build_quests_service()

    try:
        result = await service.complete_quest(user_id=current_user.id, quest_id=quest_id)

        # completed quest, this closes the active assigment
        completed_quest = result["completed_quest"]

        #Then we return a response with the new quest assigned to user
        # assigned_at will be now, status active
        new_q = result["new_assigned_quest"]
        now = datetime.now(timezone.utc)
        dummy_assignment = type(
            "Assignment",
            (),
            {"status": "active", "assigned_at": now, "completed_at": None},
        )()

        return CompleteQuestResponse(
            completed_quest_id=completed_quest.id,
            rewards=result["rewards"],
            new_assigned_quest=_to_quest_response(new_q, dummy_assignment),
        )

    except QuestNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except QuestAlreadyCompletedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    except QuestNotAssignedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("", response_model=QuestResponse, status_code=status.HTTP_201_CREATED)
async def create_quest(payload: CreateQuestRequest):
    """
    Create a quest in catalog.
    """
    service = build_quests_service()

    try:
        quest = await service.create_quest(payload.model_dump())

        # For catalog-only response, we return quest data with a dummy assignment
        now = datetime.now(timezone.utc)
        dummy_assignment = type(
            "Assignment",
            (),
            {"status": "active", "assigned_at": now, "completed_at": None},
        )()

        return _to_quest_response(quest, dummy_assignment)

    except QuestUpdateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/{quest_id}", response_model=QuestResponse)
async def update_quest(quest_id: str, payload: UpdateQuestRequest):
    """
    Update a quest in catalog.
    """
    service = build_quests_service()

    try:
        quest = await service.update_quest(quest_id, payload.model_dump(exclude_unset=True))

        now = datetime.now(timezone.utc)
        dummy_assignment = type(
            "Assignment",
            (),
            {"status": "active", "assigned_at": now, "completed_at": None},
        )()

        return _to_quest_response(quest, dummy_assignment)

    except QuestNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except QuestUpdateError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{quest_id}", response_model=DeleteQuestResponse)
async def delete_quest(quest_id: str):
    """
    Delete a quest from catalog.
    """
    service = build_quests_service()

    try:
        await service.delete_quest(quest_id)
        return DeleteQuestResponse(deleted=True)

    except QuestNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

    except QuestDeleteError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/guilds/{guild_id}/bootstrap", response_model=BootstrapGuildQuestsResponse)
async def bootstrap_guild_quests(guild_id: str, current_user: User = Depends(get_current_user)):
    """
    Endpoint to bootstrap quests for a guild.
    (Usually called from guild join flow instead.)
    """
    service = build_quests_service()

    try:
        await service.bootstrap_guild_quests(user_id=current_user.id, guild_id=guild_id)
        return BootstrapGuildQuestsResponse(bootstrapped=True)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
