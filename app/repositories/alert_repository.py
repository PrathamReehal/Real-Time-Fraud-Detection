from typing import List, Optional
import asyncpg
from app.domain.interfaces import IAlertRepository
from app.domain.models import Alert
from app.core.exceptions import DatabaseError


class AlertRepository(IAlertRepository):
    def __init__(self, connection: asyncpg.Connection):
        self.connection = connection
    
    async def get_by_id(self, id: int) -> Optional[Alert]:
        try:
            query = "SELECT * FROM alerts WHERE id = $1"
            row = await self.connection.fetchrow(query, id)
            return self._row_to_alert(row) if row else None
        except Exception as e:
            raise DatabaseError(f"Error fetching alert by id: {e}")
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Alert]:
        try:
            query = "SELECT * FROM alerts ORDER BY timestamp DESC LIMIT $1 OFFSET $2"
            rows = await self.connection.fetch(query, limit, offset)
            return [self._row_to_alert(row) for row in rows]
        except Exception as e:
            raise DatabaseError(f"Error fetching all alerts: {e}")
    
    async def get_recent(self, limit: int) -> List[Alert]:
        try:
            query = "SELECT * FROM alerts ORDER BY timestamp DESC LIMIT $1"
            rows = await self.connection.fetch(query, limit)
            return [self._row_to_alert(row) for row in rows]
        except Exception as e:
            raise DatabaseError(f"Error fetching recent alerts: {e}")
    
    async def get_high_probability(self, threshold: float) -> List[Alert]:
        try:
            query = "SELECT * FROM alerts WHERE probability > $1 ORDER BY probability DESC LIMIT 100"
            rows = await self.connection.fetch(query, threshold)
            return [self._row_to_alert(row) for row in rows]
        except Exception as e:
            raise DatabaseError(f"Error fetching high probability alerts: {e}")
    
    async def create(self, alert: Alert) -> Alert:
        try:
            query = """
                INSERT INTO alerts (nameorig, namedest, amount, type, probability, timestamp)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """
            row_id = await self.connection.fetchval(
                query, alert.name_orig, alert.name_dest, alert.amount,
                alert.type, alert.probability, alert.timestamp
            )
            alert.id = row_id
            return alert
        except Exception as e:
            raise DatabaseError(f"Error creating alert: {e}")
    
    async def delete(self, id: int) -> bool:
        try:
            query = "DELETE FROM alerts WHERE id = $1"
            result = await self.connection.execute(query, id)
            return result == "DELETE 1"
        except Exception as e:
            raise DatabaseError(f"Error deleting alert: {e}")
    
    def _row_to_alert(self, row) -> Alert:
        return Alert(
            id=row['id'],
            name_orig=row['nameorig'],
            name_dest=row['namedest'],
            amount=float(row['amount']),
            type=row['type'],
            probability=float(row['probability']),
            timestamp=row['timestamp']
        )
