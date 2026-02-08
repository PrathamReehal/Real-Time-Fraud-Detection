from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List
from app.api.schemas.transaction import TransactionCreate, TransactionResponse, TransactionListResponse
from app.api.schemas.prediction import PredictionResponse
from app.api.dependencies import get_fraud_detection_service
from app.services.fraud_detection_service import FraudDetectionService
from app.domain.models import Transaction
from app.core.exceptions import DatabaseError, NotFoundError

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    service: FraudDetectionService = Depends(get_fraud_detection_service)
):
    try:
        domain_txn = Transaction(
            step=transaction.step,
            type=transaction.type,
            amount=transaction.amount,
            name_orig=transaction.name_orig,
            oldbalance_org=transaction.oldbalance_org,
            newbalance_orig=transaction.newbalance_orig,
            name_dest=transaction.name_dest,
            oldbalance_dest=transaction.oldbalance_dest,
            newbalance_dest=transaction.newbalance_dest,
            timestamp=transaction.timestamp
        )
        
        prediction = await service.process_transaction(domain_txn)
        
        return PredictionResponse(
            transaction_id=prediction.transaction_id,
            fraud_probability=prediction.fraud_probability,
            is_fraud=prediction.is_fraud,
            timestamp=prediction.timestamp
        )
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error: {str(e)}")


@router.get("/recent", response_model=List[TransactionResponse])
async def get_recent_transactions(
    limit: int = Query(default=100, ge=1, le=1000, description="Number of transactions to retrieve"),
    service: FraudDetectionService = Depends(get_fraud_detection_service)
):
    try:
        transactions = await service.get_recent_transactions(limit)
        return [TransactionResponse(**txn.__dict__) for txn in transactions]
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: int,
    service: FraudDetectionService = Depends(get_fraud_detection_service)
):
    try:
        transaction = await service.get_transaction_by_id(transaction_id)
        if not transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        return TransactionResponse(**transaction.__dict__)
    except DatabaseError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
