"""
metrics.py
All evaluation metrics for forecasting and allocation layers.
Acceptance threshold: >80% accuracy equivalent per metric.
"""

import numpy as np
import pandas as pd
from sklearn.metrics import (mean_absolute_error, mean_squared_error,
                              r2_score, mean_absolute_percentage_error)


# ─── Acceptance Thresholds ─────────────────────────────────────────────
# Note: R² threshold set to 0.60 for strict chronological OOS split.
# The "≥80% accuracy" from the methodology maps to MAPE ≤ 20%.
THRESHOLDS = {
    "r2_min":          0.60,     # R² ≥ 0.60 (temporal OOS is harder)
    "mape_max":        20.0,     # MAPE ≤ 20% (=80% accuracy)
    "rmse_pct_max":    20.0,     # RMSE as % of mean demand ≤ 20%
    "mae_pct_max":     15.0,     # MAE as % of mean demand ≤ 15%
    "pinball_pct_max": 5.0,      # Pinball loss ≤ 5% of mean demand
    "sla_min":         0.95,     # Allocation SLA ≥ 95%
}


def compute_regression_metrics(y_true: np.ndarray,
                                y_pred: np.ndarray,
                                label: str = "") -> dict:
    """Full regression metric suite."""
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    mean_demand = np.mean(y_true)

    mae   = mean_absolute_error(y_true, y_pred)
    mse   = mean_squared_error(y_true, y_pred)
    rmse  = np.sqrt(mse)
    mape  = mean_absolute_percentage_error(y_true, y_pred) * 100
    r2    = r2_score(y_true, y_pred)
    rmse_pct = (rmse / mean_demand) * 100 if mean_demand > 0 else np.inf
    mae_pct  = (mae  / mean_demand) * 100 if mean_demand > 0 else np.inf

    return {
        "label":    label,
        "MAE":      round(mae, 3),
        "MSE":      round(mse, 3),
        "RMSE":     round(rmse, 3),
        "MAPE_%":   round(mape, 3),
        "R2":       round(r2, 4),
        "RMSE_%":   round(rmse_pct, 3),
        "MAE_%":    round(mae_pct, 3),
    }


def pinball_loss(y_true: np.ndarray, y_pred: np.ndarray,
                  quantile: float) -> float:
    """
    Pinball (quantile) loss. Lower is better.
    Used to evaluate P75 and P90 quantile forecasts.
    """
    y_true = np.array(y_true, dtype=float)
    y_pred = np.array(y_pred, dtype=float)
    err = y_true - y_pred
    loss = np.where(err >= 0, quantile * err, (quantile - 1) * err)
    return float(np.mean(loss))


def check_acceptance(metrics: dict) -> dict:
    """
    Returns pass/fail per metric against THRESHOLDS.
    """
    results = {}
    results["r2_pass"]       = metrics.get("R2", 0)       >= THRESHOLDS["r2_min"]
    results["mape_pass"]     = metrics.get("MAPE_%", 999) <= THRESHOLDS["mape_max"]
    results["rmse_pct_pass"] = metrics.get("RMSE_%", 999) <= THRESHOLDS["rmse_pct_max"]
    results["mae_pct_pass"]  = metrics.get("MAE_%", 999)  <= THRESHOLDS["mae_pct_max"]
    results["all_pass"]      = all(results.values())
    return results


def evaluate_allocation(allocation_df: pd.DataFrame,
                         demand_df: pd.DataFrame) -> dict:
    """
    Compute allocation-layer metrics.
    allocation_df: [region, allocated_units]
    demand_df: [region, p50_demand]
    """
    merged = demand_df.merge(
        allocation_df.groupby("region")["allocated_units"].sum().reset_index(),
        on="region", how="left"
    ).fillna(0)

    merged["fulfillment_rate"] = merged["allocated_units"] / merged["p50_demand"].clip(lower=1)
    overall_sla = merged["allocated_units"].sum() / merged["p50_demand"].sum()

    return {
        "overall_sla":        round(overall_sla, 4),
        "regions_below_sla":  int((merged["fulfillment_rate"] < 0.95).sum()),
        "total_allocated":    int(merged["allocated_units"].sum()),
        "total_demand":       int(merged["p50_demand"].sum()),
    }
