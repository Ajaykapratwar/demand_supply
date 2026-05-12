"""
tests/test_rules_engine.py
L5 rules engine tests.
"""

import pytest
from services.tower_svc.rules_engine import RulesEngine


@pytest.mark.unit
class TestRulesEngine:
    def setup_method(self):
        self.engine = RulesEngine()

    def test_stockout_triggers_emergency_reorder(self):
        alert = {
            "severity": "critical",
            "description": "Stockout risk for North region",
            "metric_name": "fill_rate",
            "metric_value": 0.88,
        }
        actions = self.engine.evaluate(alert)
        assert any(a["action_type"] == "emergency_reorder" for a in actions)

    def test_lead_time_violation_escalates(self):
        alert = {
            "severity": "warning",
            "description": "Lead time exceeded",
            "metric_name": "lead_time_sigma",
            "metric_value": 2.1,
        }
        actions = self.engine.evaluate(alert)
        assert any(a["action_type"] == "escalation" for a in actions)
        assert any(a["action_type"] == "safety_stock_increase" for a in actions)

    def test_bias_drift_triggers_retrain(self):
        alert = {
            "severity": "warning",
            "description": "Forecast bias detected",
            "metric_name": "forecast_bias",
            "metric_value": 7.2,
        }
        actions = self.engine.evaluate(alert)
        assert any(a["action_type"] == "model_retrain" for a in actions)

    def test_no_rules_match(self):
        alert = {
            "severity": "info",
            "description": "System healthy",
            "metric_name": "cpu_usage",
            "metric_value": 45,
        }
        actions = self.engine.evaluate(alert)
        assert len(actions) == 0

    def test_response_time_attached(self):
        alert = {
            "severity": "critical",
            "description": "Stockout risk",
            "metric_name": "fill_rate",
            "metric_value": 0.80,
        }
        actions = self.engine.evaluate(alert)
        for action in actions:
            assert "response_time_s" in action
            assert action["response_time_s"] <= 1200
