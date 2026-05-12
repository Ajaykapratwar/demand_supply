"""Unit tests for merge pipeline."""

import pytest
import pandas as pd
import numpy as np
from src.feature_store.merge_pipeline import (
    extract_year_month, aggregate_orders, aggregate_sales
)


@pytest.mark.unit
def test_extract_year_month_creates_period():
    df = pd.DataFrame({"Date": pd.to_datetime(["2020-01-15", "2020-02-20"])})
    result = extract_year_month(df)
    assert "YearMonth" in result.columns
    assert str(result["YearMonth"].iloc[0]) == "2020-01"


@pytest.mark.unit
def test_aggregate_orders_groups_by_region_month():
    df = pd.DataFrame({
        "Date": pd.to_datetime(["2020-01-01"] * 4),
        "Region": ["North", "North", "South", "South"],
        "Fulfillment_Rate_%": [0.85, 0.90, 0.80, 0.88],
        "Units_Backordered": [10, 20, 15, 5],
        "Units_Ordered": [100, 200, 150, 50],
        "Units_Fulfilled": [90, 180, 120, 44],
    })
    result = aggregate_orders(df)
    assert len(result) == 2  # North and South
    assert "Avg_Fulfillment_Rate" in result.columns


@pytest.mark.unit
def test_aggregate_sales_sums_units():
    df = pd.DataFrame({
        "Date": pd.to_datetime(["2020-01-01"] * 2),
        "Region": ["North", "North"],
        "Net_Units_Sold_TARGET": [100.0, 200.0],
        "Avg_Selling_Price_INR": [30000.0, 35000.0],
        "Discount_%": [5.0, 10.0],
        "Net_Revenue_INR": [2850000.0, 6300000.0],
    })
    result = aggregate_sales(df)
    assert result["Net_Units_Sold"].iloc[0] == 300.0
