"""
quantile_forecaster.py
Orchestrates P50/P75/P90 outputs. Computes:
- Safety stock = P90 - P50
- Risk flag if gap > 30% of P50
"""

import pandas as pd
import numpy as np
from src.forecasting.xgboost_model import build_quantile_forecasters


def generate_quantile_forecasts(X_train, y_train, X_val, y_val,
                                  X_test) -> pd.DataFrame:
    """
    Returns DataFrame with columns:
    [index, P50, P75, P90, safety_stock, risk_flag]
    """
    forecasters = build_quantile_forecasters(X_train, y_train, X_val, y_val)

    results = pd.DataFrame(index=X_test.index)
    results["P50"] = forecasters["p50"].predict(X_test)
    results["P75"] = forecasters["p75"].predict(X_test)
    results["P90"] = forecasters["p90"].predict(X_test)

    # Ensure monotonicity: P50 <= P75 <= P90
    results["P75"] = results[["P50", "P75"]].max(axis=1)
    results["P90"] = results[["P75", "P90"]].max(axis=1)

    results["safety_stock"] = results["P90"] - results["P50"]
    results["risk_flag"]    = (results["safety_stock"] / results["P50"].clip(lower=1)) > 0.30

    return results
