from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class TransactionBase(BaseModel):
    step: int = Field(..., ge=1, description="Transaction step (time unit)")
    type: str = Field(..., pattern="^(PAYMENT|TRANSFER|CASH_OUT|DEBIT|CASH_IN)$", description="Transaction type")
    amount: float = Field(..., gt=0, description="Transaction amount")
    name_orig: str = Field(..., description="Origin account name")
    oldbalance_org: float = Field(..., ge=0, description="Origin account old balance")
    newbalance_orig: float = Field(..., ge=0, description="Origin account new balance")
    name_dest: str = Field(..., description="Destination account name")
    oldbalance_dest: float = Field(..., ge=0, description="Destination account old balance")
    newbalance_dest: float = Field(..., ge=0, description="Destination account new balance")
    timestamp: datetime = Field(..., description="Transaction timestamp")


class TransactionCreate(TransactionBase):
    pass


class TransactionResponse(TransactionBase):
    id: int
    
    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    transactions: list[TransactionResponse]
    total: int
    limit: int
    offset: int
