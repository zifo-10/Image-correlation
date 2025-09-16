from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    DATABASE_URL: str
    STORAGE_KEY: str
    STORAGE_URL: str
    OPENAI_API_KEY: str
    TAVILY_API_KEY: str

    # Debug mode
    DEBUG: bool = Field(default=False)

    # Example for future expansion
    APP_NAME: str = Field(default="Zedny Product API")

    class Config:
        # Automatically read from .env file
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton settings object
settings = Settings()
