from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class AlertBase(BaseModel):
    name_orig: str = Field(..., description="Origin account name")
    name_dest: str = Field(..., description="Destination account name")
    amount: float = Field(..., gt=0, description="Transaction amount")
    type: str = Field(..., description="Transaction type")
    probability: float = Field(..., ge=0, le=1, description="Fraud probability")
    timestamp: datetime = Field(..., description="Alert timestamp")


class AlertResponse(AlertBase):
    id: int
    
    class Config:
        from_attributes = True


class AlertListResponse(BaseModel):
    alerts: list[AlertResponse]
    total: int
    limit: int
