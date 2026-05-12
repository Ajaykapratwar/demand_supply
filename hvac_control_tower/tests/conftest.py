"""
tests/conftest.py
Shared fixtures for the full test suite.
"""

import sys
import os
import pytest
import pandas as pd
import numpy as np

# Ensure project root on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "raw")


@pytest.fixture
def sample_master_df():
    """Minimal Region x YearMonth master table for unit tests."""
    rng = np.random.RandomState(42)
    regions = ["North", "South", "East", "West"]
    dates = pd.period_range("2022-01", periods=24, freq="M")
    rows = []
    for region in regions:
        for d in dates:
            rows.append({
                "Region": region,
                "YearMonth": d,
                "Net_Units_Sold": int(rng.normal(500, 100)),
                "Avg_Selling_Price": rng.uniform(15000, 50000),
                "Avg_Discount": rng.uniform(5, 25),
                "Total_Revenue": rng.uniform(5e6, 5e7),
                "Avg_Fulfillment_Rate": rng.uniform(85, 99),
                "Total_Units_Backordered": int(rng.uniform(0, 100)),
                "Total_Units_Ordered": int(rng.normal(600, 100)),
                "Total_Units_Fulfilled": int(rng.normal(550, 100)),
                "Max_Temp_C": rng.uniform(25, 45),
                "Min_Temp_C": rng.uniform(10, 25),
                "Cooling_Degree_Days": rng.uniform(50, 300),
                "Google_Trends_AC_Index": rng.uniform(20, 90),
                "Heatwave_Severity_Score": rng.uniform(0, 10),
                "Festive_Multiplier": rng.choice([1.0, 1.2, 1.5]),
                "Composite_Demand_Index": rng.uniform(30, 80),
                "Forecast_Demand_Target": rng.normal(500, 80),
                "Avg_Utilization": rng.uniform(60, 95),
                "Avg_Days_Of_Supply": rng.uniform(20, 60),
                "Total_Aged_Stock_90d": int(rng.uniform(0, 500)),
                "Avg_SLA_Compliance": rng.uniform(90, 99),
                "Total_Units_Shipped": int(rng.normal(500, 100)),
                "Avg_Distance_KM": rng.uniform(100, 1500),
                "Avg_Cost_Per_Unit": rng.uniform(50, 200),
                "Total_CO2_Kg": rng.uniform(100, 5000),
            })
    return pd.DataFrame(rows)


@pytest.fixture
def small_demand_series():
    """Simple demand series for Croston/safety-stock tests."""
    return np.array([0, 0, 5, 0, 0, 0, 3, 0, 0, 7, 0, 0, 4, 0, 0, 0, 6, 0, 0, 0, 5, 0, 0, 8])

