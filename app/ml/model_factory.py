import pickle
import joblib
from typing import Any
from app.core.config import get_settings
from app.core.exceptions import ModelLoadError


class ModelFactory:
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelFactory, cls).__new__(cls)
        return cls._instance
    
    def get_model(self) -> Any:
        if self._model is None:
            self._load_model()
        return self._model
    
    def _load_model(self):
        settings = get_settings()
        try:
            self._model = joblib.load(settings.MODEL_PATH)
        except Exception as e:
            raise ModelLoadError(f"Failed to load model: {e}")
        finally:    
            print("Loaded model type:", type(self._model))
    
    def reload_model(self):
        self._model = None
        self._load_model()
