"""Application configuration."""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"
    DB_USER: str = "admin"
    DB_PASSWORD: str = "admin"
    
    MODEL_PATH: str = "ml/fraud_model.pkl"
    FRAUD_THRESHOLD: float = 0.5
    
    API_PREFIX: str = "/api/v1"
    
    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
