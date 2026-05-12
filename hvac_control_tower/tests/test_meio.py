"""
tests/test_meio.py
L4 MEIO solver tests.
"""

import pytest
import pandas as pd
from services.policy_svc.meio_solver import build_network_data, run_meio_solver


@pytest.mark.integration
class TestMEIOSolver:
    def setup_method(self):
        self.regions = ["North", "South", "East", "West"]
        self.network = build_network_data(self.regions)
        self.branch_demands = {
            f"BRANCH-{r}": 2000 for r in self.regions
        }

    def test_solver_returns_optimal(self):
        result = run_meio_solver(
            self.network["nodes"], self.network["edges"], self.branch_demands
        )
        assert result["status"] == "Optimal"

    def test_fill_rates_above_threshold(self):
        result = run_meio_solver(
            self.network["nodes"], self.network["edges"], self.branch_demands
        )
        for branch, fr in result["fill_rates"].items():
            assert fr >= 0.95, f"Fill rate at {branch} = {fr:.2%}, expected ≥95%"

    def test_overall_fill_rate(self):
        result = run_meio_solver(
            self.network["nodes"], self.network["edges"], self.branch_demands
        )
        assert result["overall_fill_rate"] >= 0.95

    def test_allocations_non_empty(self):
        result = run_meio_solver(
            self.network["nodes"], self.network["edges"], self.branch_demands
        )
        assert not result["allocations"].empty

    def test_network_data_structure(self):
        assert "nodes" in self.network
        assert "edges" in self.network
        assert set(self.network["nodes"]["echelon"].unique()) == {"factory", "dc", "branch"}

    def test_zero_demand(self):
        """Zero demand should still return Optimal with no allocations needed."""
        zero_demands = {f"BRANCH-{r}": 0 for r in self.regions}
        result = run_meio_solver(
            self.network["nodes"], self.network["edges"], zero_demands
        )
        assert result["status"] == "Optimal"
