from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt as pyjwt

from app.auth.dependency_injection.providers import build_user_repo
from app.auth.domain.errors import UnauthorizedError
from app.core.jwt import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme)):
    """Get current user from bearer token in Authorization header."""
    #Check if Authoritation header contains bearer value
    if creds is None or creds.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    #If present we extract the token
    token = creds.credentials
    
    try:
        #Decode payload from token
        payload = decode_access_token(token)
        #Extract the subject (user id) from token's payload
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError("Token missing subject")
    except (pyjwt.ExpiredSignatureError, pyjwt.InvalidTokenError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    except UnauthorizedError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    
    #We build the repository needed to retrieve user info
    repo = build_user_repo()
    user = await repo.get_by_id(str(user_id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user
