"""
conftest.py — Shared fixtures for all test modules.
"""

import pytest
import pandas as pd
import numpy as np


@pytest.fixture(scope="session")
def sample_demand_df():
    """Minimal 60-row region×month demand DataFrame."""
    np.random.seed(42)
    regions = ["North", "South", "East", "West", "Central"]
    months = pd.period_range("2020-01", "2020-12", freq="M")
    rows = []
    for r in regions:
        for m in months:
            rows.append({
                "Region": r, "YearMonth": m,
                "Net_Units_Sold": int(np.random.normal(700, 150)),
                "Max_Temp_C": np.random.uniform(20, 45),
                "Cooling_Degree_Days": np.random.uniform(0, 500),
                "Google_Trends_AC_Index": np.random.uniform(5, 100),
                "Composite_Demand_Index": np.random.uniform(0.1, 1.0),
                "Festive_Multiplier": np.random.choice([1.0, 1.2, 1.5]),
            })
    return pd.DataFrame(rows)


@pytest.fixture(scope="session")
def sample_warehouse_df():
    """5 warehouses with capacity and inventory."""
    np.random.seed(0)
    return pd.DataFrame({
        "warehouse_id":     [f"WH{i:03d}" for i in range(1, 6)],
        "capacity":         [5000, 4000, 6000, 3500, 4500],
        "current_inventory":[3000, 2500, 4000, 2000, 3000],
        "safety_stock":     [300,  250,  400,  200,  300],
    })


@pytest.fixture(scope="session")
def sample_region_df():
    return pd.DataFrame({
        "region":     ["North", "South", "East", "West", "Central"],
        "p50_demand": [1200, 800, 600, 700, 500],
        "p90_demand": [1500, 1000, 750, 900, 650],
    })


@pytest.fixture(scope="session")
def sample_cost_matrix(sample_warehouse_df, sample_region_df):
    np.random.seed(1)
    rows = []
    for wh in sample_warehouse_df["warehouse_id"]:
        for r in sample_region_df["region"]:
            rows.append({
                "warehouse_id": wh,
                "region": r,
                "cost_per_unit": round(np.random.uniform(400, 800), 2),
            })
    return pd.DataFrame(rows)
