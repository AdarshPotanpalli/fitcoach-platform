from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_USERNAME : str
    DATABASE_PASSWORD : str
    DATABASE_IP : str
    DATABASE_NAME : str
    DATABASE_PORT: str
    SECRET_KEY: str
    ALGORITHM :str
    ACCESS_TOKEN_EXPIRE_MINUTES : int

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()