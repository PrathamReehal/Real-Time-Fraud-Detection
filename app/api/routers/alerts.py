from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List
from app.api.schemas.alert import AlertResponse, AlertListResponse
from app.api.dependencies import get_fraud_detection_service
from app.services.fraud_detection_service import FraudDetectionService
from app.core.exceptions import DatabaseError

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("/recent", response_model=List[AlertResponse])
async def get_recent_alerts(
    limit: int = Query(default=20, ge=1, le=100, description="Number of alerts to retrieve"),
    service: FraudDetectionService = Depends(get_fraud_detection_service)
):
    try:
        alerts = await service.get_recent_alerts(limit)
        return [AlertResponse(**alert.__dict__) for alert in alerts]
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/high-risk", response_model=List[AlertResponse])
async def get_high_risk_alerts(
    threshold: float = Query(default=0.7, ge=0.0, le=1.0, description="Minimum probability threshold"),
    service: FraudDetectionService = Depends(get_fraud_detection_service)
):
    try:
        alerts = await service.get_high_risk_alerts(threshold)
        return [AlertResponse(**alert.__dict__) for alert in alerts]
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: int,
    service: FraudDetectionService = Depends(get_fraud_detection_service)
):
    try:
        alert = await service.get_alert_by_id(alert_id)
        if not alert:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
        return AlertResponse(**alert.__dict__)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
