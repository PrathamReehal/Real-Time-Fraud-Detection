"""Domain models."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Transaction:
    step: int
    type: str
    amount: float
    name_orig: str
    oldbalance_org: float
    newbalance_orig: float
    name_dest: str
    oldbalance_dest: float
    newbalance_dest: float
    timestamp: datetime
    id: Optional[int] = None


@dataclass
class Alert:
    name_orig: str
    name_dest: str
    amount: float
    type: str
    probability: float
    timestamp: datetime
    id: Optional[int] = None


@dataclass
class Prediction:
    transaction_id: Optional[int]
    probability: float
    is_fraud: bool
    timestamp: datetime
