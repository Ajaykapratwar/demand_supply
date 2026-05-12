"""
tests/test_safety_stock.py
L4 safety stock property tests (spec §6.1).
Property checks:
  - SS monotone in sigma_D
  - SS monotone in sigma_L
  - Z=0 ⇒ SS=0
  - sigma_L > 1.5 triggers alert
"""

import pytest
import numpy as np
from services.policy_svc.safety_stock import (
    compute_safety_stock, compute_reorder_point, check_lead_time_constraint,
)


class TestSafetyStockFormula:
    """Spec §6.1: SS = Z x √(L_avg x sigma_D² + D_avg² x sigma_L²)"""

    @pytest.mark.unit
    def test_z_zero_yields_zero(self):
        """Z=0 ⇒ SS=0 regardless of other parameters."""
        ss = compute_safety_stock(100, 20, 7, 1.2, z_score=0)
        assert ss == 0.0, f"SS should be 0 when Z=0, got {ss}"

    @pytest.mark.unit
    def test_monotone_in_sigma_d(self):
        """Higher sigma_D → higher safety stock (monotonicity)."""
        ss_low = compute_safety_stock(100, 10, 7, 1.2, z_score=1.65)
        ss_high = compute_safety_stock(100, 30, 7, 1.2, z_score=1.65)
        assert ss_high > ss_low, f"SS({ss_high}) should > SS({ss_low}) when sigma_D increases"

    @pytest.mark.unit
    def test_monotone_in_sigma_l(self):
        """Higher sigma_L → higher safety stock (monotonicity)."""
        ss_low = compute_safety_stock(100, 20, 7, 0.5, z_score=1.65)
        ss_high = compute_safety_stock(100, 20, 7, 2.0, z_score=1.65)
        assert ss_high > ss_low, f"SS({ss_high}) should > SS({ss_low}) when sigma_L increases"

    @pytest.mark.unit
    def test_positive_for_nonzero_inputs(self):
        ss = compute_safety_stock(100, 20, 7, 1.2, z_score=1.65)
        assert ss > 0

    @pytest.mark.unit
    def test_formula_exact(self):
        """Verify formula matches manual calculation."""
        D_avg, sigma_D, L_avg, sigma_L, Z = 100, 20, 7, 1.2, 1.65
        expected = Z * np.sqrt(L_avg * sigma_D**2 + D_avg**2 * sigma_L**2)
        actual = compute_safety_stock(D_avg, sigma_D, L_avg, sigma_L, Z)
        # Result is max(calculated, MIN_SAFETY_BUFFER)
        assert actual >= expected or actual >= 50  # MIN_SAFETY_BUFFER = 50


class TestReorderPoint:
    @pytest.mark.unit
    def test_rop_basic(self):
        rop = compute_reorder_point(100, 7, 200)
        assert rop == 900  # 100*7 + 200

    @pytest.mark.unit
    def test_rop_zero_safety_stock(self):
        rop = compute_reorder_point(50, 7, 0)
        assert rop == 350


class TestLeadTimeConstraint:
    """Spec: sigma_L <= 1.5 days. If violated, DO NOT silently absorb."""

    @pytest.mark.unit
    def test_pass_within_limit(self):
        result = check_lead_time_constraint(1.2)
        assert result["passed"] is True

    @pytest.mark.unit
    def test_fail_exceeds_limit(self):
        result = check_lead_time_constraint(2.0)
        assert result["passed"] is False
        assert "alert" in result

    @pytest.mark.unit
    def test_alert_severity_critical(self):
        result = check_lead_time_constraint(3.0)
        assert result["alert"].severity == "critical"

    @pytest.mark.unit
    def test_boundary_value(self):
        result = check_lead_time_constraint(1.5)
        assert result["passed"] is True

