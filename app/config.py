from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    #App configuration
    APP_NAME: str = "TFB API"
    ENV: str = "development"

    #MongoDB configuration
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "tfb_database"

    #JWT configuration
    JWT_SECRET: str = "mysecret1234"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )   

settings = Settings()