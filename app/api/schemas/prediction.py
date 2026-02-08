from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PredictionResponse(BaseModel):
    transaction_id: Optional[int] = Field(None, description="Transaction ID")
    fraud_probability: float = Field(..., ge=0, le=1, description="Fraud probability score")
    is_fraud: bool = Field(..., description="Whether transaction is classified as fraud")
    timestamp: datetime = Field(..., description="Prediction timestamp")
    
    class Config:
        from_attributes = True


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    database: str
    model: str
