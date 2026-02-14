from typing import Optional

from pydantic import BaseModel


# Responses
class StatsResponse(BaseModel):
    """
    Stats response schema
    """
    strength: int
    focus: int
    resilience: int


class ProgressResponse(BaseModel):
    """
    Progression response schema
    """
    user_id: str
    level: int
    xp: int
    gold: int
    stats: StatsResponse
    created_at: str
    updated_at: Optional[str] = None


class GetProgressResponse(BaseModel):
    """
    Response for GET /progression/me
    """
    progression: ProgressResponse