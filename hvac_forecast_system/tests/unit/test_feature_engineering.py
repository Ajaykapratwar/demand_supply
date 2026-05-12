"""Unit tests for feature engineering."""

import pytest
import pandas as pd
import numpy as np
from src.feature_store.feature_engineering import (
    add_lag_features, add_rolling_features, add_cyclic_time_features
)


@pytest.fixture
def simple_ts():
    months = pd.period_range("2020-01", "2020-12", freq="M")
    return pd.DataFrame({
        "Region": ["North"] * 12,
        "YearMonth": months,
        "Net_Units_Sold": list(range(100, 1300, 100)),
    })


@pytest.mark.unit
def test_lag_features_length_preserved(simple_ts):
    result = add_lag_features(simple_ts, "Net_Units_Sold", "Region")
    assert len(result) == len(simple_ts)


@pytest.mark.unit
def test_lag_1_is_previous_month(simple_ts):
    result = add_lag_features(simple_ts, "Net_Units_Sold", "Region")
    # Row index 1: lag_1 should equal row 0 value
    assert result["Net_Units_Sold_lag_1"].iloc[1] == simple_ts["Net_Units_Sold"].iloc[0]


@pytest.mark.unit
def test_lag_1_first_row_is_nan(simple_ts):
    result = add_lag_features(simple_ts, "Net_Units_Sold", "Region")
    assert pd.isna(result["Net_Units_Sold_lag_1"].iloc[0])


@pytest.mark.unit
def test_cyclic_features_range(simple_ts):
    result = add_cyclic_time_features(simple_ts, "YearMonth")
    assert result["month_sin"].between(-1, 1).all()
    assert result["month_cos"].between(-1, 1).all()


@pytest.mark.unit
def test_rolling_mean_3_correct_value(simple_ts):
    result = add_rolling_features(simple_ts, "Net_Units_Sold", "Region")
    # Row 3 rolling mean should be mean of rows 0,1,2 (shifted by 1)
    expected = np.mean([100, 200, 300])
    assert abs(result["Net_Units_Sold_roll_mean_3"].iloc[3] - expected) < 1e-5
