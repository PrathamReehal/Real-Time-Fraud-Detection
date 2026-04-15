"""FastAPI application with all routes."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List

from app.config import get_settings
from app.database import db, TransactionRepository, AlertRepository, DatabaseError
from app.service import FraudService, ModelLoader, ModelLoadError
from app.models import Transaction
from app.schemas import (
    TransactionCreate, TransactionResponse, 
    AlertResponse, PredictionResponse, HealthResponse
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Fraud Detection API...")
    await db.connect()
    yield
    logger.info("Shutting down...")
    await db.disconnect()


app = FastAPI(
    title="Fraud Detection API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Exception Handlers
# =============================================================================
@app.exception_handler(ModelLoadError)
async def handle_model_error(request: Request, exc: ModelLoadError):
    return JSONResponse(status_code=503, content={"error": "ML model unavailable"})

@app.exception_handler(DatabaseError)
async def handle_db_error(request: Request, exc: DatabaseError):
    logger.error(f"Database error: {exc}")
    return JSONResponse(status_code=500, content={"error": "Database error"})


# =============================================================================
# Health
# =============================================================================
@app.get(f"{settings.API_PREFIX}/health", response_model=HealthResponse, tags=["health"])
async def health():
    model_status = "loaded" if ModelLoader.is_loaded() else "not loaded"
    try:
        ModelLoader.get_model()
        model_status = "loaded"
    except Exception:
        model_status = "error"
    
    return HealthResponse(
        status="healthy",
        database="connected" if db.is_connected else "disconnected",
        model=model_status
    )


# =============================================================================
# Transactions
# =============================================================================
@app.post(
    f"{settings.API_PREFIX}/transactions",
    response_model=PredictionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["transactions"]
)
async def create_transaction(txn: TransactionCreate):
    async with db.connection() as conn:
        service = FraudService(TransactionRepository(conn), AlertRepository(conn))
        domain_txn = Transaction(
            step=txn.step,
            type=txn.type,
            amount=txn.amount,
            name_orig=txn.name_orig,
            oldbalance_org=txn.oldbalance_org,
            newbalance_orig=txn.newbalance_orig,
            name_dest=txn.name_dest,
            oldbalance_dest=txn.oldbalance_dest,
            newbalance_dest=txn.newbalance_dest,
            timestamp=txn.timestamp
        )
        prediction = await service.process_transaction(domain_txn)
        return PredictionResponse(
            transaction_id=prediction.transaction_id,
            probability=prediction.probability,
            is_fraud=prediction.is_fraud,
            timestamp=prediction.timestamp
        )


@app.get(
    f"{settings.API_PREFIX}/transactions/recent",
    response_model=List[TransactionResponse],
    tags=["transactions"]
)
async def get_recent_transactions(limit: int = Query(100, ge=1, le=1000)):
    async with db.connection() as conn:
        service = FraudService(TransactionRepository(conn), AlertRepository(conn))
        txns = await service.get_recent_transactions(limit)
        return [TransactionResponse(**t.__dict__) for t in txns]


@app.get(
    settings.API_PREFIX + "/transactions/{txn_id}",
    response_model=TransactionResponse,
    tags=["transactions"]
)
async def get_transaction(txn_id: int):
    async with db.connection() as conn:
        service = FraudService(TransactionRepository(conn), AlertRepository(conn))
        txn = await service.get_transaction(txn_id)
        if not txn:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return TransactionResponse(**txn.__dict__)


# =============================================================================
# Alerts
# =============================================================================
@app.get(
    f"{settings.API_PREFIX}/alerts/recent",
    response_model=List[AlertResponse],
    tags=["alerts"]
)
async def get_recent_alerts(limit: int = Query(20, ge=1, le=100)):
    async with db.connection() as conn:
        service = FraudService(TransactionRepository(conn), AlertRepository(conn))
        alerts = await service.get_recent_alerts(limit)
        return [AlertResponse(**a.__dict__) for a in alerts]


@app.get(
    f"{settings.API_PREFIX}/alerts/high-risk",
    response_model=List[AlertResponse],
    tags=["alerts"]
)
async def get_high_risk_alerts(threshold: float = Query(0.7, ge=0, le=1)):
    async with db.connection() as conn:
        service = FraudService(TransactionRepository(conn), AlertRepository(conn))
        alerts = await service.get_high_risk_alerts(threshold)
        return [AlertResponse(**a.__dict__) for a in alerts]


@app.get(
    settings.API_PREFIX + "/alerts/{alert_id}",
    response_model=AlertResponse,
    tags=["alerts"]
)
async def get_alert(alert_id: int):
    async with db.connection() as conn:
        service = FraudService(TransactionRepository(conn), AlertRepository(conn))
        alert = await service.get_alert(alert_id)
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        return AlertResponse(**alert.__dict__)


@app.get("/")
async def root():
    return {"message": "Fraud Detection API", "docs": "/docs"}
