"""Unit tests for safety stock calculations."""

import pytest
import pandas as pd
import numpy as np
from src.allocation.safety_stock import compute_safety_stock, compute_reorder_point


@pytest.fixture
def forecast_df():
    return pd.DataFrame({
        "Region": ["North", "South"],
        "P50": [1000.0, 600.0],
        "P75": [1150.0, 720.0],
        "P90": [1300.0, 800.0],
    })


@pytest.mark.unit
def test_safety_stock_equals_p90_minus_p50(forecast_df):
    result = compute_safety_stock(forecast_df)
    assert result["safety_stock_units"].iloc[0] == pytest.approx(300.0)
    assert result["safety_stock_units"].iloc[1] == pytest.approx(200.0)


@pytest.mark.unit
def test_safety_stock_non_negative(forecast_df):
    df = forecast_df.copy()
    df["P90"] = df["P50"] - 10   # P90 < P50 (edge case)
    result = compute_safety_stock(df)
    assert (result["safety_stock_units"] >= 0).all()


@pytest.mark.unit
def test_reorder_point_exceeds_safety_stock(forecast_df):
    ss_df = compute_safety_stock(forecast_df)
    rop_df = compute_reorder_point(ss_df, lead_time_days=7)
    assert (rop_df["reorder_point"] >= rop_df["safety_stock_units"]).all()
