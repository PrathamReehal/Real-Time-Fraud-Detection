from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "postgres"
    DB_USER: str = "admin"
    DB_PASSWORD: str = "admin"
    
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC: str = "transactions"
    
    MODEL_PATH: str = "/Users/prathamreehal/Desktop/practice/first_project/Real-Time-Fraud-Detection/app/ml/fraud_detection_pipeline.pkl"
    FRAUD_THRESHOLD: float = 0.5
    
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Fraud Detection API"
    DEBUG: bool = True
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
