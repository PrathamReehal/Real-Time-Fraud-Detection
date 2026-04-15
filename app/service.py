"""Business logic for fraud detection."""
import pickle
import joblib
import pandas as pd
from datetime import datetime
from typing import List, Optional
from app.config import get_settings
from app.models import Transaction, Alert, Prediction
from app.database import TransactionRepository, AlertRepository


class ModelLoadError(Exception):
    pass


class ModelLoader:
    """Singleton model loader."""
    _model = None
    
    @classmethod
    def get_model(cls):
        if cls._model is None:
            settings = get_settings()
            try:
                with open(settings.MODEL_PATH, "rb") as f:
                    cls._model = pickle.load(f)
            except Exception:
                try:
                    cls._model = joblib.load(settings.MODEL_PATH)
                except Exception as e:
                    raise ModelLoadError(f"Failed to load model: {e}")
        return cls._model
    
    @classmethod
    def is_loaded(cls) -> bool:
        return cls._model is not None


class FraudService:
    """Fraud detection business logic."""
    
    def __init__(self, txn_repo: TransactionRepository, alert_repo: AlertRepository):
        self._txn_repo = txn_repo
        self._alert_repo = alert_repo
        self._settings = get_settings()
    
    async def process_transaction(self, txn: Transaction) -> Prediction:
        """Save transaction, predict fraud, create alert if needed."""
        saved_txn = await self._txn_repo.create(txn)
        prediction = self._predict(saved_txn)
        
        if prediction.is_fraud:
            alert = Alert(
                name_orig=txn.name_orig,
                name_dest=txn.name_dest,
                amount=txn.amount,
                type=txn.type,
                probability=prediction.probability,
                timestamp=txn.timestamp
            )
            await self._alert_repo.create(alert)
        
        return prediction
    
    def _predict(self, txn: Transaction) -> Prediction:
        """Run ML model on transaction."""
        model = ModelLoader.get_model()
        
        # Model was trained with only these features (step, nameOrig, nameDest were dropped)
        data = pd.DataFrame([{
            'type': txn.type,
            'amount': txn.amount,
            'oldbalanceOrg': txn.oldbalance_org,
            'newbalanceOrig': txn.newbalance_orig,
            'oldbalanceDest': txn.oldbalance_dest,
            'newbalanceDest': txn.newbalance_dest
        }])
        
        if hasattr(model, "predict_proba"):
            prob = float(model.predict_proba(data)[0, 1])
        else:
            prob = float(model.predict(data)[0])
        
        return Prediction(
            transaction_id=txn.id,
            probability=prob,
            is_fraud=prob > self._settings.FRAUD_THRESHOLD,
            timestamp=datetime.utcnow()
        )
    
    async def get_recent_transactions(self, limit: int = 100) -> List[Transaction]:
        return await self._txn_repo.get_recent(limit)
    
    async def get_transaction(self, id: int) -> Optional[Transaction]:
        return await self._txn_repo.get_by_id(id)
    
    async def get_recent_alerts(self, limit: int = 20) -> List[Alert]:
        return await self._alert_repo.get_recent(limit)
    
    async def get_high_risk_alerts(self, threshold: float = 0.7) -> List[Alert]:
        return await self._alert_repo.get_high_risk(threshold)
    
    async def get_alert(self, id: int) -> Optional[Alert]:
        return await self._alert_repo.get_by_id(id)
