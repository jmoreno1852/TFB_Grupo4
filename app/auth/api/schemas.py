from datetime import datetime
from pydantic import BaseModel, EmailStr, Field

#Schemas for authentication requests and responses
class RegisterRequest(BaseModel):
    #Ensure the format of email and password 
    email: EmailStr
    password: str = Field(min_length=8, max_length=23)

class RegisterResponse(BaseModel):
    #Return ID for redirection or confirmation
    id: str 
    email: EmailStr
    created_at: datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=23)

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"