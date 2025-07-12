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
    COOKIE_SECRET : str
    COOKIE_PREFIX : str
    OPENAI_API_KEY : str
    GOOGLE_REDIRECT_URI: str
    FRONTEND_URL: str
    GOOGLE_CREDENTIALS_ENCRYPTION_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()