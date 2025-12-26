from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from app.config import settings

def create_access_token(
    payload: dict[str, Any],
    expires_minutes: Optional[int] = None
) -> str:
    """Create JWT token with given payload and expiration time"""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(
        #Use expires_minutes value, if not provided use default from settings
        minutes=expires_minutes or settings.JWT_EXPIRE_MINUTES
    )

    to_encode = payload.copy()
    to_encode.update({
        #Expire Value
        "exp": expire, 
        #Issued at value
        "iat": int(now.timestamp())}
    )
    #JWT encoding
    return jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )

def decode_access_token(token: str) -> dict[str, Any]:
    """Decode JWT, validate it. Raise exceptions if validation fails"""
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALGORITHM]
    )

def extract_bearer_token(
    authorization_header: str | None
) -> str | None:
    """Extract bearer token from header"""
    if not authorization_header:
        return None
    
    components = authorization_header.split(" ")
    #Check integrity of header structure
    if len(components) != 2:
        return None
    
    scheme, token = components
    #Check if the scheme is bearer
    if scheme.lower() != "bearer":
        return None
    return token