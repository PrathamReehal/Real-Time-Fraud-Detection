from fastapi import APIRouter, Depends
from datetime import datetime
from app.api.schemas.prediction import HealthCheckResponse
from app.core.database import db_manager
from app.ml.model_factory import ModelFactory
from app.api.dependencies import get_model_factory

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/", response_model=HealthCheckResponse)
async def health_check(model_factory: ModelFactory = Depends(get_model_factory)):
    db_status = "connected" if db_manager._pool else "disconnected"
    
    try:
        model = model_factory.get_model()
        model_status = "loaded"
    except Exception as e:
        model_status = f"error: {str(e)}"
    
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        database=db_status,
        model=model_status
    )
