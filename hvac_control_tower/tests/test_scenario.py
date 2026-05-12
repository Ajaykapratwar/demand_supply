"""
tests/test_scenario.py
L2 scenario tests (spec §6.5 verification).
Verification: copper +10% scenario completes in <30s.
"""

import pytest
from services.twin_svc.scenario import ScenarioEngine, ScenarioInput, ScenarioOutput


@pytest.mark.scenario
class TestScenarioEngine:
    def setup_method(self):
        self.engine = ScenarioEngine()

    def test_copper_shock_completes_under_30s(self):
        """Spec §4.2: copper +10% must complete in <30s."""
        result = self.engine.run_scenario(
            ScenarioInput("copper_shock", 90, {"price_delta_pct": 10.0})
        )
        assert result.simulation_time_s < 30.0
        assert result.cost_delta_pct > 0
        assert len(result.fill_rate_trajectory) == 90
        assert len(result.recommended_actions) > 0

    def test_early_freeze_trajectory(self):
        result = self.engine.run_scenario(
            ScenarioInput("early_freeze", 90, {"demand_surge_pct": 40.0})
        )
        assert isinstance(result, ScenarioOutput)
        assert len(result.inventory_trajectory) == 90

    def test_seer2_transition(self):
        result = self.engine.run_scenario(
            ScenarioInput("seer2_transition", 90, {"obsolescence_pct": 30.0})
        )
        assert result.cost_delta_pct > 0
        assert "LastTimeBuy" in result.recommended_actions[0]

    def test_supplier_outage(self):
        result = self.engine.run_scenario(
            ScenarioInput("supplier_outage", 90,
                          {"outage_days": 30, "sigma_l_multiplier": 2.0})
        )
        assert any("sigma_L" in a for a in result.recommended_actions)

    def test_unknown_scenario_raises(self):
        with pytest.raises(ValueError, match="Unknown scenario"):
            self.engine.run_scenario(ScenarioInput("nonexistent", 30))

    def test_all_scenarios_under_30s(self):
        """Verify all 4 canonical scenarios complete within performance budget."""
        scenarios = [
            ScenarioInput("copper_shock", 90, {"price_delta_pct": 10.0}),
            ScenarioInput("early_freeze", 90, {"demand_surge_pct": 40.0}),
            ScenarioInput("seer2_transition", 90, {"obsolescence_pct": 30.0}),
            ScenarioInput("supplier_outage", 90, {"outage_days": 30}),
        ]
        for s in scenarios:
            result = self.engine.run_scenario(s)
            assert result.simulation_time_s < 30.0, \
                f"{s.name} took {result.simulation_time_s}s (limit: 30s)"

