from fastapi import FastAPI
from contextlib import asynccontextmanager


from app.config import settings
from app.database import close_db
from app.auth.api.router import router as auth_router
from app.users.api.router import router as users_router
from app.auth.dependency_injection.providers import build_user_repo

#Imports to clear cache for testing purposes with TestClient
from app.auth.dependency_injection.providers import clear_caches as clear_auth_caches


CACHE_CLEAR_FUNCTIONS = [
    clear_auth_caches,
]

#Startup event to ensure indexes uniqueness in the database
@asynccontextmanager
async def lifespan(app: FastAPI):
    #lifespan manager on startup 
    repo = build_user_repo()
    #startup ensure indexes uniqueness of email values
    await repo.ensure_indexes()
    #yield this point to startup completion
    yield
    #lifespan manager on shutdown
    
    #clear caches for testing purposes
    for clear_cache in CACHE_CLEAR_FUNCTIONS:
        clear_cache()
    #close database connection
    await close_db()

#Create the app with FastAPI
def create_app() -> FastAPI:
    #Start FatAPI app with lifespan manager
    app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

    #Routers
    app.include_router(auth_router)
    app.include_router(users_router)
    #Health check endpoint for testing purposes
    @app.get("/health")
    async def health():
        return {"status": "ok"}
    
    return app
    
#Create app instance of FastAPI
app = create_app()
