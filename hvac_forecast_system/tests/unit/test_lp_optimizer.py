"""Unit tests for PuLP allocation optimizer."""

import pytest
import pandas as pd
import numpy as np
from src.allocation.lp_optimizer import run_allocation_optimizer


@pytest.mark.unit
def test_optimizer_returns_dataframe(sample_warehouse_df, sample_region_df,
                                      sample_cost_matrix):
    result = run_allocation_optimizer(
        sample_warehouse_df, sample_region_df, sample_cost_matrix
    )
    assert isinstance(result, pd.DataFrame)
    assert "allocated_units" in result.columns
    assert "warehouse_id" in result.columns


@pytest.mark.unit
def test_allocation_satisfies_demand(sample_warehouse_df, sample_region_df,
                                      sample_cost_matrix):
    result = run_allocation_optimizer(
        sample_warehouse_df, sample_region_df, sample_cost_matrix
    )
    region_totals = result.groupby("region")["allocated_units"].sum()
    for _, row in sample_region_df.iterrows():
        r = row["region"]
        allocated = region_totals.get(r, 0)
        assert allocated >= row["p50_demand"] * 0.95, (
            f"Region {r}: allocated {allocated} < 95% of demand {row['p50_demand']}"
        )


@pytest.mark.unit
def test_allocation_respects_warehouse_capacity(sample_warehouse_df,
                                                  sample_region_df,
                                                  sample_cost_matrix):
    result = run_allocation_optimizer(
        sample_warehouse_df, sample_region_df, sample_cost_matrix
    )
    wh_totals = result.groupby("warehouse_id")["allocated_units"].sum()
    cap = sample_warehouse_df.set_index("warehouse_id")["capacity"].to_dict()
    for wh, total in wh_totals.items():
        assert total <= cap[wh] + 1, (
            f"Warehouse {wh}: allocated {total} > capacity {cap[wh]}"
        )


@pytest.mark.unit
def test_no_negative_allocations(sample_warehouse_df, sample_region_df,
                                   sample_cost_matrix):
    result = run_allocation_optimizer(
        sample_warehouse_df, sample_region_df, sample_cost_matrix
    )
    assert (result["allocated_units"] >= 0).all()
