from datetime import datetime
from typing import  Dict, List, Literal, Optional

from pydantic import BaseModel, Field


QuestStatus = Literal["active", "completed"]

# Responses
class QuestResponse(BaseModel):
    """
    Quest response schema for both catalog and user quests
    """
    id: str
    guild_id: str
    title: str
    description: Optional[str] = None
    difficulty: int = 1
    xp_reward: int = 10
    gold_reward: int = 0
    is_active: bool = True
    weight: Optional[int] = None
    cooldown_hours: Optional[int] = None

    status: QuestStatus = "active"
    assigned_at: datetime
    completed_at: Optional[datetime] = None


class ListUserQuestsResponse(BaseModel):
    """
    List user active quests response
    """
    quests: List[QuestResponse]


class CompleteQuestResponse(BaseModel):
    """
    Response when completing a quest:
    - rewards earned
    - new quest assigned
    """
    completed_quest_id: str
    rewards: Dict[str, int]
    new_assigned_quest: QuestResponse


class BootstrapGuildQuestsResponse(BaseModel):
    """
    Response when bootstrapping guild quests (optional endpoint)
    """
    bootstrapped: bool = True


# Requests CRUD

class CreateQuestRequest(BaseModel):
    """
    Create quest in catalog
    """
    guild_id: str
    title: str = Field(..., min_length=3, max_length=80)
    description: Optional[str] = Field(default=None, max_length=280)
    difficulty: int = Field(default=1, ge=1, le=10)
    xp_reward: int = Field(default=10, ge=0)
    gold_reward: int = Field(default=0, ge=0)
    is_active: bool = True
    weight: Optional[int] = Field(default=None, ge=1)
    cooldown_hours: Optional[int] = Field(default=None, ge=0)


class UpdateQuestRequest(BaseModel):
    """
    Update quest in catalog, partial update allowed
    """
    guild_id: Optional[str] = None
    title: Optional[str] = Field(default=None, min_length=3, max_length=80)
    description: Optional[str] = Field(default=None, max_length=280)
    difficulty: Optional[int] = Field(default=None, ge=1, le=10)
    xp_reward: Optional[int] = Field(default=None, ge=0)
    gold_reward: Optional[int] = Field(default=None, ge=0)
    is_active: Optional[bool] = None
    weight: Optional[int] = Field(default=None, ge=1)
    cooldown_hours: Optional[int] = Field(default=None, ge=0)

#Response CRUD
class DeleteQuestResponse(BaseModel):
    """
    Response when deleting a quest from catalog
    """
    deleted: bool = True