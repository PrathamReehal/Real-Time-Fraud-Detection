from fastapi import Depends
import asyncpg
from app.core.database import get_db_connection
from app.repositories.transaction_repository import TransactionRepository
from app.repositories.alert_repository import AlertRepository
from app.services.fraud_detection_service import FraudDetectionService
from app.ml.model_factory import ModelFactory


async def get_transaction_repository(
    conn: asyncpg.Connection = Depends(get_db_connection)
) -> TransactionRepository:
    return TransactionRepository(conn)


async def get_alert_repository(
    conn: asyncpg.Connection = Depends(get_db_connection)
) -> AlertRepository:
    return AlertRepository(conn)


def get_model_factory() -> ModelFactory:
    return ModelFactory()


async def get_fraud_detection_service(
    transaction_repo: TransactionRepository = Depends(get_transaction_repository),
    alert_repo: AlertRepository = Depends(get_alert_repository),
    model_factory: ModelFactory = Depends(get_model_factory)
) -> FraudDetectionService:
    return FraudDetectionService(transaction_repo, alert_repo, model_factory)
