"""API request/response schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TransactionCreate(BaseModel):
    step: int = Field(..., ge=0)
    type: str = Field(..., pattern="^(PAYMENT|TRANSFER|CASH_OUT|DEBIT|CASH_IN)$")
    amount: float = Field(..., gt=0)
    name_orig: str
    oldbalance_org: float = Field(..., ge=0)
    newbalance_orig: float = Field(..., ge=0)
    name_dest: str
    oldbalance_dest: float = Field(..., ge=0)
    newbalance_dest: float = Field(..., ge=0)
    timestamp: datetime


class TransactionResponse(TransactionCreate):
    id: int
    
    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    id: int
    name_orig: str
    name_dest: str
    amount: float
    type: str
    probability: float = Field(..., ge=0, le=1)
    timestamp: datetime
    
    class Config:
        from_attributes = True


class PredictionResponse(BaseModel):
    transaction_id: Optional[int] = None
    probability: float = Field(..., ge=0, le=1)
    is_fraud: bool
    timestamp: datetime


class HealthResponse(BaseModel):
    status: str
    database: str
    model: str
