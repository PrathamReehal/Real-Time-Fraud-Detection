from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from app.core.exceptions import (
    FraudDetectionException,
    ModelLoadError,
    DatabaseError,
    ValidationError,
    NotFoundError
)
import logging

logger = logging.getLogger(__name__)


def add_exception_handlers(app: FastAPI):
    
    @app.exception_handler(ModelLoadError)
    async def model_load_error_handler(request: Request, exc: ModelLoadError):
        logger.error(f"Model load error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "ML model unavailable", "error": str(exc)}
        )
    
    @app.exception_handler(DatabaseError)
    async def database_error_handler(request: Request, exc: DatabaseError):
        logger.error(f"Database error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Database error occurred", "error": str(exc)}
        )
    
    @app.exception_handler(NotFoundError)
    async def not_found_error_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Resource not found", "error": str(exc)}
        )
    
    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": "Validation error", "error": str(exc)}
        )
    
    @app.exception_handler(FraudDetectionException)
    async def fraud_detection_error_handler(request: Request, exc: FraudDetectionException):
        logger.error(f"Fraud detection error: {exc}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Fraud detection error", "error": str(exc)}
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unexpected error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error", "error": str(exc)}
        )
