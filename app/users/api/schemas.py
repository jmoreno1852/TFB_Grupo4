from datetime import datetime
from typing import Optional 

from pydantic import BaseModel, Field
#For future use of avatar_url
#from pydantic import HttpUrl

class UserSettingsSchema (BaseModel):
    """
    Settings schema for Response
    """
    language: str 
    timezone: str
    theme: str

class UserMeResponse(BaseModel):
    """
    Profile Response for current user
    """
    user_id: str
    username: str
    display_name: str
    bio: Optional[str] = None
    #avatar_url: Optional[HttpUrl] = None
    settings: UserSettingsSchema
    created_at: datetime
    updated_at: datetime
#Create request not needed as profile is created empty at first GET
class UpdateSettingsRequest(BaseModel):
    """
    Partial update for settings, all fields optional.
    """
    language: Optional[str] = Field(default=None, min_length=1, max_length=16)
    timezone: Optional[str] = Field(default=None, min_length=1, max_length=64)
    theme: Optional[str] = Field(default=None, min_length=1, max_length=16)


class UpdateProfileRequest(BaseModel):
    """
    Partial update for profile, all fields optional.
    """
    username: Optional[str] = Field(default=None, min_length=3, max_length=30)
    display_name: Optional[str] = Field(default=None, min_length=1, max_length=40)
    bio: Optional[str] = Field(default=None, max_length=280)

    # keep as str as  domain will validate too
    #avatar_url: Optional[str] = Field(default=None, max_length=2048)

    # nested settings update
    settings: Optional[UpdateSettingsRequest] = None
