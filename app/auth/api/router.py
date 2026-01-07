from fastapi import APIRouter, Depends, HTTPException, status
#Import chemas for expected requests and responses
from app.auth.api.schemas import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    TokenResponse,
)
from app.auth.api.deps import get_current_user
from app.auth.dependency_injection.providers import build_auth_service
from app.auth.domain.errors import UserAlreadyExistsError, InvalidCredentialsError

#Define router for /auth endpoints
router = APIRouter(prefix="/auth", tags=["auth"])

#Register endpoint
@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    service = build_auth_service()
    try:
        user = await service.register(payload.email, payload.password)
        return RegisterResponse(id=user.id, email=user.email, created_at=user.created_at)
    except UserAlreadyExistsError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

#Login endpoint
@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    service = build_auth_service()
    try:
        token = await service.login(payload.email, payload.password)
        return TokenResponse(access_token=token)
    except InvalidCredentialsError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

#Get current user endpoint
@router.get("/me", response_model=RegisterResponse)
async def me(current_user=Depends(get_current_user)):
    #Reuse of RegisterResponse, we could also use a specific UserMeResponse schema
    return RegisterResponse(id=current_user.id, email=current_user.email, created_at=current_user.created_at)
