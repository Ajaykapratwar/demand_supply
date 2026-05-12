"""
reports.py
Generate metric summary reports as CSV/dict.
"""

import pandas as pd
from pathlib import Path
from src.evaluation.metrics import compute_regression_metrics, pinball_loss, evaluate_allocation


def generate_forecast_report(y_true, forecasts: dict, output_path: str = None) -> pd.DataFrame:
    """
    Generate a summary report for multiple quantile forecasts.
    forecasts: {"p50": array, "p75": array, "p90": array}
    """
    rows = []

    # Point forecast metrics (P50)
    if "p50" in forecasts:
        metrics = compute_regression_metrics(y_true, forecasts["p50"], label="XGBoost P50")
        rows.append(metrics)

    # Quantile metrics
    for q, label in [(0.75, "p75"), (0.90, "p90")]:
        if label in forecasts:
            pb = pinball_loss(y_true, forecasts[label], quantile=q)
            rows.append({
                "label": f"XGBoost {label.upper()}",
                "pinball_loss": round(pb, 3),
                "quantile": q,
            })

    report = pd.DataFrame(rows)

    if output_path:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        report.to_csv(output_path, index=False)

    return report
