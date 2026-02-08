from typing import List
import pandas as pd
from app.domain.models import Transaction, Alert, FraudPrediction
from app.domain.interfaces import ITransactionRepository, IAlertRepository
from app.ml.model_factory import ModelFactory
from app.core.config import get_settings
from app.core.exceptions import ModelLoadError
from datetime import datetime


class FraudDetectionService:
    def __init__(
        self,
        transaction_repo: ITransactionRepository,
        alert_repo: IAlertRepository,
        model_factory: ModelFactory
    ):
        self.transaction_repo = transaction_repo
        self.alert_repo = alert_repo
        self.model_factory = model_factory
        self.settings = get_settings()
    
    async def predict_fraud(self, transaction: Transaction) -> FraudPrediction:
        try:
            model = self.model_factory.get_model()
            
            data = pd.DataFrame([{
                'step': transaction.step,
                'type': transaction.type,
                'amount': transaction.amount,
                'nameOrig': transaction.name_orig,
                'oldbalanceOrg': transaction.oldbalance_org,
                'newbalanceOrig': transaction.newbalance_orig,
                'nameDest': transaction.name_dest,
                'oldbalanceDest': transaction.oldbalance_dest,
                'newbalanceDest': transaction.newbalance_dest
            }])
            
            if hasattr(model, "predict_proba"):
                probability = float(model.predict_proba(data)[0, 1])
            else:
                probability = float(model.predict(data)[0])
            
            is_fraud = probability > self.settings.FRAUD_THRESHOLD
            
            return FraudPrediction(
                transaction_id=transaction.transaction_id,
                fraud_probability=probability,
                is_fraud=is_fraud,
                timestamp=datetime.utcnow()
            )
        except Exception as e:
            raise ModelLoadError(f"Error during fraud prediction: {e}")
    
    async def process_transaction(self, transaction: Transaction) -> FraudPrediction:
        saved_txn = await self.transaction_repo.create(transaction)
        
        prediction = await self.predict_fraud(saved_txn)
        
        if prediction.is_fraud:
            alert = Alert(
                name_orig=transaction.name_orig,
                name_dest=transaction.name_dest,
                amount=transaction.amount,
                type=transaction.type,
                probability=prediction.fraud_probability,
                timestamp=transaction.timestamp
            )
            await self.alert_repo.create(alert)
        
        return prediction
    
    async def get_recent_alerts(self, limit: int = 20) -> List[Alert]:
        return await self.alert_repo.get_recent(limit)
    
    async def get_high_risk_alerts(self, threshold: float = 0.7) -> List[Alert]:
        return await self.alert_repo.get_high_probability(threshold)
    
    async def get_recent_transactions(self, limit: int = 100) -> List[Transaction]:
        return await self.transaction_repo.get_recent(limit)
    
    async def get_transaction_by_id(self, txn_id: int) -> Transaction:
        return await self.transaction_repo.get_by_id(txn_id)
    
    async def get_alert_by_id(self, alert_id: int) -> Alert:
        return await self.alert_repo.get_by_id(alert_id)
