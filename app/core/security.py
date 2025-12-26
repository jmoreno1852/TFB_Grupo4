from passlib.context import CryptContext

#Define values for password hashing
_pwd_context = CryptContext(
    #Secure implementation through bcrypt algorithm
    schemes=["bcrypt"], 
    deprecated="auto"
)

def hash_password(password: str) -> str:
    """Hash a password in plain text"""
    return _pwd_context.hash(password)

def verify_password(password: str, password_hash: str) -> bool:
    """Verify plain text password agains hashed password in db"""
    return _pwd_context.verify(password, password_hash)