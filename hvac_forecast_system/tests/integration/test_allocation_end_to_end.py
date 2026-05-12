"""
Integration test: allocation end-to-end from forecasts to LP solution.
"""

import pytest
import pandas as pd
import numpy as np
from src.allocation.safety_stock import compute_safety_stock, compute_reorder_point
from src.allocation.lp_optimizer import run_allocation_optimizer
from src.evaluation.metrics import evaluate_allocation


@pytest.mark.integration
def test_allocation_end_to_end(sample_warehouse_df, sample_region_df, sample_cost_matrix):
    """Full flow: safety stock → LP → evaluation."""
    # Simulate quantile forecasts
    forecast_df = sample_region_df.rename(columns={
        "region": "Region", "p50_demand": "P50", "p90_demand": "P90"
    })
    forecast_df["P75"] = (forecast_df["P50"] + forecast_df["P90"]) / 2

    # Compute safety stock
    ss_df = compute_safety_stock(forecast_df)
    assert "safety_stock_units" in ss_df.columns
    assert (ss_df["safety_stock_units"] >= 0).all()

    # Run LP
    allocation = run_allocation_optimizer(
        sample_warehouse_df, sample_region_df, sample_cost_matrix
    )
    assert len(allocation) > 0

    # Evaluate allocation
    eval_result = evaluate_allocation(allocation, sample_region_df)
    assert eval_result["overall_sla"] >= 0.95
    assert eval_result["regions_below_sla"] == 0
