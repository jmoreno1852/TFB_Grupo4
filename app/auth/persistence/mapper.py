#File to map the objects used in auth from and to the database
from bson import ObjectId
from app.auth.domain.entities import User

def user_to_db(user: User) -> dict:
    """Map a User entity to a document for MongoDB"""
    #No need to set up an id for the user as it is generated once it is inserted into MongoDB database
    return {
        "email": user.email,
        "password_hash": user.password_hash,
        "created_at": user.created_at,
    }

def db_to_user(doc: dict) -> User:
    """Map a document from the MongoDB to a User entity"""
    return User(
        id=str(doc["_id"]),
        email=doc["email"],
        password_hash=doc["password_hash"],
        created_at=doc["created_at"]

    )
   


