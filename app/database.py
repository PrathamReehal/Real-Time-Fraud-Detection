"""Database connection and repositories."""
from typing import List, Optional
from contextlib import asynccontextmanager
import asyncpg
from app.config import get_settings
from app.models import Transaction, Alert


class DatabaseError(Exception):
    pass


class Database:
    """Manages database connection pool."""
    
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        if self._pool is None:
            settings = get_settings()
            self._pool = await asyncpg.create_pool(
                host=settings.DB_HOST,
                port=settings.DB_PORT,
                database=settings.DB_NAME,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                min_size=5,
                max_size=20
            )
    
    async def disconnect(self):
        if self._pool:
            await self._pool.close()
            self._pool = None
    
    @asynccontextmanager
    async def connection(self):
        if not self._pool:
            await self.connect()
        async with self._pool.acquire() as conn:
            yield conn
    
    @property
    def is_connected(self) -> bool:
        return self._pool is not None


db = Database()


class TransactionRepository:
    """Data access for transactions."""
    
    def __init__(self, conn: asyncpg.Connection):
        self._conn = conn
    
    async def create(self, txn: Transaction) -> Transaction:
        query = """
            INSERT INTO transactions 
            (step, type, amount, nameorig, oldbalanceorg, newbalanceorig,
             namedest, oldbalancedest, newbalancedest, timestamp)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
            RETURNING transaction_id
        """
        txn.id = await self._conn.fetchval(
            query, txn.step, txn.type, txn.amount, txn.name_orig,
            txn.oldbalance_org, txn.newbalance_orig, txn.name_dest,
            txn.oldbalance_dest, txn.newbalance_dest, txn.timestamp
        )
        return txn
    
    async def get_by_id(self, id: int) -> Optional[Transaction]:
        row = await self._conn.fetchrow(
            "SELECT * FROM transactions WHERE transaction_id = $1", id
        )
        return self._to_model(row) if row else None
    
    async def get_recent(self, limit: int = 100) -> List[Transaction]:
        rows = await self._conn.fetch(
            "SELECT * FROM transactions ORDER BY timestamp DESC LIMIT $1", limit
        )
        return [self._to_model(r) for r in rows]
    
    def _to_model(self, row) -> Transaction:
        return Transaction(
            id=row['transaction_id'],
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


class AlertRepository:
    """Data access for alerts."""
    
    def __init__(self, conn: asyncpg.Connection):
        self._conn = conn
    
    async def create(self, alert: Alert) -> Alert:
        query = """
            INSERT INTO alerts (nameorig, namedest, amount, type, probability, timestamp)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING id
        """
        alert.id = await self._conn.fetchval(
            query, alert.name_orig, alert.name_dest, alert.amount,
            alert.type, alert.probability, alert.timestamp
        )
        return alert
    
    async def get_by_id(self, id: int) -> Optional[Alert]:
        row = await self._conn.fetchrow("SELECT * FROM alerts WHERE id = $1", id)
        return self._to_model(row) if row else None
    
    async def get_recent(self, limit: int = 20) -> List[Alert]:
        rows = await self._conn.fetch(
            "SELECT * FROM alerts ORDER BY timestamp DESC LIMIT $1", limit
        )
        return [self._to_model(r) for r in rows]
    
    async def get_high_risk(self, threshold: float = 0.7) -> List[Alert]:
        rows = await self._conn.fetch(
            "SELECT * FROM alerts WHERE probability > $1 ORDER BY probability DESC LIMIT 100",
            threshold
        )
        return [self._to_model(r) for r in rows]
    
    def _to_model(self, row) -> Alert:
        return Alert(
            id=row['id'],
            name_orig=row['nameorig'],
            name_dest=row['namedest'],
            amount=float(row['amount']),
            type=row['type'],
            probability=float(row['probability']),
            timestamp=row['timestamp']
        )
