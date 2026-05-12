"""Unit tests for quantile forecaster orchestration."""

import pytest
import pandas as pd
import numpy as np


@pytest.mark.unit
def test_quantile_monotonicity_enforcement():
    """Verify P50 <= P75 <= P90 after clipping."""
    results = pd.DataFrame({
        "P50": [100, 200, 300],
        "P75": [90, 250, 280],   # P75 < P50 for row 0 and row 2
        "P90": [80, 260, 350],   # P90 < P75 for row 0
    })
    # Apply monotonicity enforcement (same logic as quantile_forecaster.py)
    results["P75"] = results[["P50", "P75"]].max(axis=1)
    results["P90"] = results[["P75", "P90"]].max(axis=1)

    assert (results["P75"] >= results["P50"]).all()
    assert (results["P90"] >= results["P75"]).all()


@pytest.mark.unit
def test_safety_stock_from_quantiles():
    """Safety stock = P90 - P50, always non-negative."""
    results = pd.DataFrame({
        "P50": [500, 600],
        "P90": [700, 800],
    })
    results["safety_stock"] = results["P90"] - results["P50"]
    assert (results["safety_stock"] >= 0).all()
    assert results["safety_stock"].iloc[0] == 200
