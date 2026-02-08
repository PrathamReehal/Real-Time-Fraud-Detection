from abc import ABC, abstractmethod
from typing import List, Optional, Generic, TypeVar
from app.domain.models import Transaction, Alert

T = TypeVar('T')


class IRepository(ABC, Generic[T]):
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[T]:
        pass
    
    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        pass
    
    @abstractmethod
    async def create(self, entity: T) -> T:
        pass
    
    @abstractmethod
    async def delete(self, id: int) -> bool:
        pass


class ITransactionRepository(IRepository[Transaction]):
    @abstractmethod
    async def get_recent(self, limit: int) -> List[Transaction]:
        pass
    
    @abstractmethod
    async def get_by_type(self, txn_type: str) -> List[Transaction]:
        pass


class IAlertRepository(IRepository[Alert]):
    @abstractmethod
    async def get_high_probability(self, threshold: float) -> List[Alert]:
        pass
    
    @abstractmethod
    async def get_recent(self, limit: int) -> List[Alert]:
        pass
