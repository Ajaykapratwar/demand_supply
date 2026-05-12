"""
model_registry.py
Save/load trained XGBoost models to/from JSON files.
"""

import json
from pathlib import Path
from src.forecasting.xgboost_model import XGBoostDemandForecaster


MODEL_DIR = Path("models")


def save_model(forecaster: XGBoostDemandForecaster, name: str) -> str:
    """Save XGBoost model to JSON. Returns path."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    path = MODEL_DIR / f"{name}.json"
    forecaster.model.save_model(str(path))
    return str(path)


def load_model(name: str, quantile: float = 0.5) -> XGBoostDemandForecaster:
    """Load XGBoost model from JSON."""
    path = MODEL_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"Model file not found: {path}")
    forecaster = XGBoostDemandForecaster(quantile=quantile)
    forecaster.model.load_model(str(path))
    forecaster.is_fitted = True
    return forecaster
