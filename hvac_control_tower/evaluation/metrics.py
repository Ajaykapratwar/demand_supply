"""
evaluation/metrics.py
Evaluation metrics for all layers. Matches spec §10 success criteria.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (mean_absolute_error, mean_squared_error,
                              r2_score, mean_absolute_percentage_error)

# Success criteria from spec §10
SUCCESS_CRITERIA = {
    "forecast_accuracy_min": 0.80,    # 1 - WAPE ≥ 80%
    "forecast_bias_max": 5.0,         # ±5%
    "r2_min": 0.91,                   # Equipment-demand R²
    "fill_rate_critical_min": 0.96,   # ≥96%
    "inventory_reduction_min": 0.15,  # 15%
    "inventory_reduction_max": 0.30,  # 30%
    "turnover_min": 4.0,             # 4.0x/yr
    "turnover_max": 6.0,             # 6.0x/yr
    "carrying_cost_min": 0.18,       # 18%
    "carrying_cost_max": 0.25,       # 25%
    "sigma_l_max": 1.5,             # days
    "orchestration_latency_max": 30,  # seconds
    "edge_latency_p99_max": 10,      # ms
}


def compute_regression_metrics(y_true, y_pred, label="") -> dict:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mean_demand = np.mean(y_true)

    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    r2 = r2_score(y_true, y_pred)
    mape = mean_absolute_percentage_error(y_true, y_pred) * 100
    wape = np.sum(np.abs(y_true - y_pred)) / np.sum(np.abs(y_true)) if np.sum(np.abs(y_true)) > 0 else 1.0

    return {
        "label": label,
        "MAE": round(mae, 3),
        "RMSE": round(rmse, 3),
        "R2": round(r2, 4),
        "MAPE_%": round(mape, 3),
        "WAPE": round(wape, 4),
        "accuracy_1_minus_WAPE": round(1 - wape, 4),
        "RMSE_%": round((rmse / mean_demand * 100) if mean_demand > 0 else 999, 3),
        "MAE_%": round((mae / mean_demand * 100) if mean_demand > 0 else 999, 3),
    }


def compute_bias(y_true, y_pred) -> float:
    """Forecast bias as percentage. Positive = over-forecast."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    total = np.sum(y_true)
    if total == 0:
        return 0.0
    return float((np.sum(y_pred) - np.sum(y_true)) / total * 100)


def pinball_loss(y_true, y_pred, quantile: float) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    err = y_true - y_pred
    loss = np.where(err >= 0, quantile * err, (quantile - 1) * err)
    return float(np.mean(loss))


def check_acceptance(metrics: dict) -> dict:
    """Check all spec §10 success criteria."""
    results = {}
    results["r2_pass"] = metrics.get("R2", 0) >= SUCCESS_CRITERIA["r2_min"]
    results["accuracy_pass"] = metrics.get("accuracy_1_minus_WAPE", 0) >= SUCCESS_CRITERIA["forecast_accuracy_min"]
    results["mape_pass"] = metrics.get("MAPE_%", 999) <= 20.0
    bias = abs(metrics.get("bias_pct", 0))
    results["bias_pass"] = bias <= SUCCESS_CRITERIA["forecast_bias_max"]
    results["all_pass"] = all(results.values())
    return results

