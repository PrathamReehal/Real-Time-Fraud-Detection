from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from app.core.config import get_settings
from app.core.database import db_manager
from app.api.routers import transactions, alerts, health
from app.api.middleware.error_handler import add_exception_handlers
from app.api.middleware.logging_middleware import LoggingMiddleware

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Fraud Detection API...")
    await db_manager.connect()
    logger.info("Database connection established")
    yield
    logger.info("Shutting down Fraud Detection API...")
    await db_manager.disconnect()
    logger.info("Database connection closed")


settings = get_settings()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Real-time fraud detection API with ML-powered predictions",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(LoggingMiddleware)

add_exception_handlers(app)

app.include_router(health.router, prefix=settings.API_V1_PREFIX)
app.include_router(transactions.router, prefix=settings.API_V1_PREFIX)
app.include_router(alerts.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "message": "Fraud Detection API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health"
    }
