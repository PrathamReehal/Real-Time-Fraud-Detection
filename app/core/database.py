from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
import asyncpg
from asyncpg import Pool
from app.core.config import get_settings
from app.core.exceptions import DatabaseError


class DatabaseManager:
    def __init__(self):
        self.settings = get_settings()
        self._pool: Optional[Pool] = None
    
    async def connect(self):
        if self._pool is None:
            try:
                self._pool = await asyncpg.create_pool(
                    host=self.settings.DB_HOST,
                    port=self.settings.DB_PORT,
                    database=self.settings.DB_NAME,
                    user=self.settings.DB_USER,
                    password=self.settings.DB_PASSWORD,
                    min_size=5,
                    max_size=20
                )
            except Exception as e:
                raise DatabaseError(f"Failed to connect to database: {e}")
    
    async def disconnect(self):
        if self._pool:
            await self._pool.close()
            self._pool = None
    
    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        if not self._pool:
            await self.connect()
        try:
            async with self._pool.acquire() as connection:
                yield connection
        except Exception as e:
            raise DatabaseError(f"Database connection error: {e}")


db_manager = DatabaseManager()


async def get_db_connection():
    async with db_manager.get_connection() as conn:
        yield conn
