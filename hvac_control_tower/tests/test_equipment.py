"""
tests/test_equipment.py
L2 equipment model tests.
"""

import pytest
from services.twin_svc.equipment import (
    compute_degraded_cop, compute_failure_probability,
    check_eol_status, generate_equipment_fleet, EQUIPMENT_PROFILES,
)


@pytest.mark.unit
class TestEquipmentModels:
    def test_cop_degrades_with_age(self):
        profile = EQUIPMENT_PROFILES["chiller"]
        cop_new = compute_degraded_cop(profile, 0)
        cop_old = compute_degraded_cop(profile, 15)
        assert cop_new > cop_old

    def test_cop_degrades_with_temperature(self):
        profile = EQUIPMENT_PROFILES["chiller"]
        cop_normal = compute_degraded_cop(profile, 5, 30.0)
        cop_hot = compute_degraded_cop(profile, 5, 45.0)
        assert cop_normal > cop_hot

    def test_failure_probability_increases_with_age(self):
        profile = EQUIPMENT_PROFILES["ahu"]
        prob_new = compute_failure_probability(profile, 1, 1000)
        prob_old = compute_failure_probability(profile, 14, 40000)
        assert prob_old > prob_new

    def test_failure_probability_bounded(self):
        profile = EQUIPMENT_PROFILES["rtu"]
        prob = compute_failure_probability(profile, 100, 1000000)
        assert 0.0 <= prob <= 1.0

    def test_eol_detection(self):
        result = check_eol_status(19.5, 20.0)
        assert result["is_eol"] is True
        assert result["last_time_buy"] is True

    def test_not_eol(self):
        result = check_eol_status(5.0, 20.0)
        assert result["is_eol"] is False

    def test_critical_urgency(self):
        result = check_eol_status(19.9, 20.0)
        assert result["urgency"] == "critical"

    def test_fleet_generation(self):
        fleet = generate_equipment_fleet(n_units=100)
        assert len(fleet) == 100
        assert "equipment_id" in fleet.columns
        assert "cop_actual" in fleet.columns
        assert "failure_prob" in fleet.columns
