from typing import List, Optional
import asyncpg
from app.domain.interfaces import ITransactionRepository
from app.domain.models import Transaction
from app.core.exceptions import DatabaseError, NotFoundError


class TransactionRepository(ITransactionRepository):
    def __init__(self, connection: asyncpg.Connection):
        self.connection = connection
    
    async def get_by_id(self, id: int) -> Optional[Transaction]:
        try:
            query = "SELECT * FROM transactions WHERE transaction_id = $1"
            row = await self.connection.fetchrow(query, id)
            return self._row_to_transaction(row) if row else None
        except Exception as e:
            raise DatabaseError(f"Error fetching transaction by id: {e}")
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Transaction]:
        try:
            query = "SELECT * FROM transactions ORDER BY timestamp DESC LIMIT $1 OFFSET $2"
            rows = await self.connection.fetch(query, limit, offset)
            return [self._row_to_transaction(row) for row in rows]
        except Exception as e:
            raise DatabaseError(f"Error fetching all transactions: {e}")
    
    async def get_recent(self, limit: int) -> List[Transaction]:
        try:
            query = "SELECT * FROM transactions ORDER BY timestamp DESC LIMIT $1"
            rows = await self.connection.fetch(query, limit)
            return [self._row_to_transaction(row) for row in rows]
        except Exception as e:
            raise DatabaseError(f"Error fetching recent transactions: {e}")
    
    async def get_by_type(self, txn_type: str) -> List[Transaction]:
        try:
            query = "SELECT * FROM transactions WHERE type = $1 ORDER BY timestamp DESC LIMIT 100"
            rows = await self.connection.fetch(query, txn_type)
            return [self._row_to_transaction(row) for row in rows]
        except Exception as e:
            raise DatabaseError(f"Error fetching transactions by type: {e}")
    
    async def create(self, transaction: Transaction) -> Transaction:
        try:
            query = """
                INSERT INTO transactions (step, type, amount, nameorig, oldbalanceorg, 
                                         newbalanceorig, namedest, oldbalancedest, 
                                         newbalancedest, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
                RETURNING transaction_id
            """
            row_id = await self.connection.fetchval(
                query, transaction.step, transaction.type, transaction.amount,
                transaction.name_orig, transaction.oldbalance_org, 
                transaction.newbalance_orig, transaction.name_dest,
                transaction.oldbalance_dest, transaction.newbalance_dest,
                transaction.timestamp
            )
            transaction.transaction_id = row_id
            return transaction
        except Exception as e:
            raise DatabaseError(f"Error creating transaction: {e}")
    
    async def delete(self, id: int) -> bool:
        try:
            query = "DELETE FROM transactions WHERE transaction_id = $1"
            result = await self.connection.execute(query, id)
            return result == "DELETE 1"
        except Exception as e:
            raise DatabaseError(f"Error deleting transaction: {e}")
    
    def _row_to_transaction(self, row) -> Transaction:
        return Transaction(
            transaction_id=row['transaction_id'],
            step=row['step'],
            type=row['type'],
            amount=float(row['amount']),
            name_orig=row['nameorig'],
            oldbalance_org=float(row['oldbalanceorg']),
            newbalance_orig=float(row['newbalanceorig']),
            name_dest=row['namedest'],
            oldbalance_dest=float(row['oldbalancedest']),
            newbalance_dest=float(row['newbalancedest']),
            timestamp=row['timestamp']
        )
