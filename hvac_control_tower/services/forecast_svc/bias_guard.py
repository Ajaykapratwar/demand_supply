"""
forecast_svc/bias_guard.py
L3: 30-day rolling bias guardrail (spec §4.3).
CI fails if |bias| > 5%.
"""

import numpy as np
import pandas as pd
from contracts.events import AnomalyAlert, EventType
from datetime import datetime, timezone
import uuid


def compute_rolling_bias(y_true: np.ndarray, y_pred: np.ndarray,
                         window: int = 30) -> pd.Series:
    """
    Compute rolling bias as (pred - actual) / actual.
    Positive = over-forecasting, Negative = under-forecasting.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    errors = y_pred - y_true
    actual_abs = np.abs(y_true)
    actual_abs = np.where(actual_abs == 0, 1, actual_abs)  # avoid div by zero
    bias_pct = errors / actual_abs * 100

    return pd.Series(bias_pct).rolling(window=window, min_periods=1).mean()


def check_bias_threshold(y_true: np.ndarray, y_pred: np.ndarray,
                         threshold_pct: float = 5.0) -> dict:
    """
    Check if current bias exceeds threshold.
    Returns pass/fail and current bias value.
    """
    rolling_bias = compute_rolling_bias(y_true, y_pred)
    current_bias = float(rolling_bias.iloc[-1]) if len(rolling_bias) > 0 else 0.0
    max_abs_bias = float(rolling_bias.abs().max()) if len(rolling_bias) > 0 else 0.0

    passed = abs(current_bias) <= threshold_pct

    result = {
        "current_bias_pct": round(current_bias, 3),
        "max_abs_bias_pct": round(max_abs_bias, 3),
        "threshold_pct": threshold_pct,
        "passed": passed,
    }

    return result


def create_bias_alert(bias_result: dict, model_name: str = "") -> AnomalyAlert:
    """Create an anomaly alert if bias threshold is breached."""
    return AnomalyAlert(
        event_id=str(uuid.uuid4())[:12],
        timestamp=datetime.now(timezone.utc).isoformat(),
        event_type=EventType.ANOMALY_ALERT.value,
        source_service="forecast-svc",
        severity="warning" if abs(bias_result["current_bias_pct"]) <= 10 else "critical",
        metric_name=f"forecast_bias_{model_name}",
        metric_value=bias_result["current_bias_pct"],
        threshold=bias_result["threshold_pct"],
        description=f"Model {model_name} bias at {bias_result['current_bias_pct']:.1f}% "
                    f"(threshold: ±{bias_result['threshold_pct']}%)",
        recommended_action="Trigger model retraining",
    )

