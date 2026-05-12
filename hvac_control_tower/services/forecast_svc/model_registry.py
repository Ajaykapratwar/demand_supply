"""
forecast_svc/model_registry.py
L3: Model versioning and persistence.
Saves/loads LightGBM models with metadata.
"""

import json
from pathlib import Path
from datetime import datetime, timezone
import lightgbm as lgb


MODEL_DIR = Path("models")


def save_model(model: lgb.LGBMRegressor, name: str, metrics: dict = None) -> str:
    """Save LightGBM model + metadata. Returns path."""
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model_path = MODEL_DIR / f"{name}.txt"
    meta_path = MODEL_DIR / f"{name}_meta.json"

    model.booster_.save_model(str(model_path))

    meta = {
        "name": name,
        "saved_at": datetime.now(timezone.utc).isoformat(),
        "n_features": model.n_features_,
        "metrics": metrics or {},
    }
    meta_path.write_text(json.dumps(meta, indent=2))

    return str(model_path)


def load_model(name: str) -> lgb.Booster:
    """Load LightGBM model from file."""
    model_path = MODEL_DIR / f"{name}.txt"
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found: {model_path}")
    return lgb.Booster(model_file=str(model_path))


def list_models() -> list:
    """List all saved models."""
    if not MODEL_DIR.exists():
        return []
    return [p.stem for p in MODEL_DIR.glob("*.txt")]

