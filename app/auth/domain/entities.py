from dataclasses import dataclass
from datetime import datetime
from typing import Optional

#User entity for authentication and registration
#Using dataclass for immutability
@dataclass(frozen=True) 
class User:
    id: str
    email: str
    password_hash: str
    created_at: datetime
