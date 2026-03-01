from fastapi import FastAPI
from contextlib import asynccontextmanager


from app.config import settings
from app.database import close_db
#Auth imports
from app.auth.api.router import router as auth_router
from app.auth.dependency_injection.providers import build_user_repo
#Users imports
from app.users.api.router import router as users_router
from app.users.dependency_injection.providers import build_user_profile_repo
# Guilds imports
from app.guilds.api.router import router as guilds_router
from app.guilds.dependency_injection.providers import build_guild_repository, build_membership_repository
# Quest imports
from app.quests.api.router import router as quests_router
from app.quests.dependency_injection.providers import build_quest_catalog_repository, build_user_quest_repository
#Progression imports
from app.progression.api.router import router as progression_router
from app.progression.dependency_injection.providers import build_progression_repository
#Inventory imports
from app.inventory.api.router import router as inventory_router
from app.inventory.dependency_injection.providers import build_inventory_repository
#Shop imports
from app.shop.api.router import router as shop_router
from app.shop.dependency_injection.providers import build_shop_rotation_repository
#House imports
from app.house.api.router import router as house_router
from app.house.dependency_injection.providers import build_house_repository

#Imports to clear cache for testing purposes with TestClient
from app.auth.dependency_injection.providers import clear_caches as clear_auth_caches
from app.users.dependency_injection.providers import clear_users_caches
from app.guilds.dependency_injection.providers import clear_caches as clear_guilds_caches
from app.quests.dependency_injection.providers import clear_caches as clear_quests_caches
from app.progression.dependency_injection.providers import clear_caches as clear_progression_caches
from app.inventory.dependency_injection.providers import clear_caches as clear_inventory_caches
from app.shop.dependency_injection.providers import clear_caches as clear_shop_caches
from app.house.dependency_injection.providers import clear_caches as clear_house_caches


CACHE_CLEAR_FUNCTIONS = [
    clear_auth_caches,
    clear_users_caches,
    clear_guilds_caches,
    clear_quests_caches,
    clear_progression_caches,
    clear_inventory_caches,
    clear_shop_caches,
    clear_house_caches,
]

#Startup event to ensure indexes uniqueness in the database
@asynccontextmanager
async def lifespan(app: FastAPI):
    #lifespan manager on startup 
    #Auth Repository
    repo_user = build_user_repo()

    #Users Profile Repository
    repo_profile = build_user_profile_repo()

    #Guilds Repository
    repo_guild = build_guild_repository()
    repo_membership = build_membership_repository()

    #Quests Repository
    repo_quest_catalog = build_quest_catalog_repository()
    repo_user_quest = build_user_quest_repository()

    #Progression Repository
    repo_progression = build_progression_repository()   

    #Inventory Repository
    repo_inventory = build_inventory_repository()

    #Shop Repository
    repo_shop_rotation = build_shop_rotation_repository()

    #House Repository
    repo_house = build_house_repository()
    
    #startup ensure indexes uniqueness of email values
    await repo_user.ensure_initialized()
    await repo_profile.ensure_initialized()

    # startup ensure indexes for guilds/memberships
    await repo_guild.ensure_initialized()
    await repo_membership.ensure_initialized()

    # startup ensure indexes for quests
    await repo_quest_catalog.ensure_initialized()
    await repo_user_quest.ensure_initialized()

    # startup ensure indexes for progression
    await repo_progression.ensure_initialized()

    # startup ensure indexes for inventory
    await repo_inventory.ensure_initialized()

    # startup ensure indexes for shop
    await repo_shop_rotation.ensure_initialized()

    # startup ensure indexes for house
    await repo_house.ensure_initialized()

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
    #Start FastAPI app with lifespan manager
    app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)

    #Routers
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(guilds_router)
    app.include_router(quests_router)
    app.include_router(progression_router)
    app.include_router(inventory_router)
    app.include_router(shop_router)
    app.include_router(house_router)
    #Health check endpoint for testing purposes
    @app.get("/health")
    async def health():
        return {"status": "ok"}
    
    return app
    
#Create app instance of FastAPI
app = create_app()
