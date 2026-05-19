from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    # App
    APP_NAME: str = Field(default="TFB API")
    #Development | production | testing
    ENV: str = Field(default="development")  

    # Mongo
    MONGO_URI: str = Field(default="mongodb://localhost:27017")
    MONGO_DB_NAME: str = Field(default="tfb_database")

    # JWT
    JWT_SECRET: str = Field(default="dev-secret-change-me")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRE_MINUTES: int = Field(default=30)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,  #Defining case sensitivity for settings fields
    )

settings = Settings()