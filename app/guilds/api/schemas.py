from typing import List, Optional

from pydantic import BaseModel, Field

#Responses
#Reponse with values of guild entity
class GuildResponse(BaseModel):
    """
    Guild response schema
    """
    id: str
    name: str
    description: Optional[str] = None

class CreateGuildResponse(BaseModel):
    """
    Response when creating a guild
    """
    guild: GuildResponse

class DeleteGuildResponse(BaseModel):
    """
    Response when deleting a guild
    """
    deleted: bool = True

class ListGuildsResponse(BaseModel):
    """
    List existing Guilds response
    """
    guilds: List[GuildResponse]

#Requests
class JoinGuildRequest(BaseModel):
    """
    Join and Leave guild request
    """
    guild_id: str 

class CreateGuildRequest(BaseModel):
    """
    Create guild request
    """
    name: str = Field(..., min_length=3, max_length=50)
    description: Optional[str] = Field(default=None, max_length=280)


