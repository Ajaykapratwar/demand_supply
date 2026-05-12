"""
tower_svc/rules_engine.py
L5: Autonomous response rules engine (spec §4.5).
Triggers within 30s for logistics events, 5-20 min for mission-critical failures.
"""

from datetime import datetime, timezone
from typing import Optional
from contracts.events import AnomalyAlert, ReorderDecision, EventType
import uuid


class Rule:
    """A single autonomous response rule."""

    def __init__(self, name: str, condition, action, response_time_s: int = 30):
        self.name = name
        self.condition = condition  # callable(alert) -> bool
        self.action = action        # callable(alert) -> list[decisions]
        self.response_time_s = response_time_s


class RulesEngine:
    """Evaluates alerts against rules and produces autonomous decisions."""

    def __init__(self):
        self.rules: list[Rule] = []
        self._register_default_rules()

    def _register_default_rules(self):
        """Register the spec-defined autonomous response rules."""

        # Rule 1: Stockout risk → emergency reorder
        self.rules.append(Rule(
            name="stockout_emergency_reorder",
            condition=lambda a: (
                a.get("severity") in ("critical", "warning")
                and "stockout" in a.get("description", "").lower()
            ),
            action=self._action_emergency_reorder,
            response_time_s=30,
        ))

        # Rule 2: Lead-time violation → escalate + increase safety stock
        self.rules.append(Rule(
            name="lead_time_violation",
            condition=lambda a: (
                "lead_time" in a.get("metric_name", "")
                and a.get("metric_value", 0) > 1.5
            ),
            action=self._action_lead_time_escalation,
            response_time_s=30,
        ))

        # Rule 3: Bias drift → trigger retraining
        self.rules.append(Rule(
            name="bias_drift_retrain",
            condition=lambda a: (
                "bias" in a.get("metric_name", "")
                and abs(a.get("metric_value", 0)) > 5
            ),
            action=self._action_retrain_model,
            response_time_s=300,  # 5 min
        ))

        # Rule 4: Equipment EOL → LastTimeBuy
        self.rules.append(Rule(
            name="eol_last_time_buy",
            condition=lambda a: "eol" in a.get("description", "").lower(),
            action=self._action_last_time_buy,
            response_time_s=1200,  # 20 min
        ))

    def evaluate(self, alert: dict) -> list[dict]:
        """Evaluate an alert against all rules. Returns triggered actions."""
        actions = []
        for rule in self.rules:
            if rule.condition(alert):
                rule_actions = rule.action(alert)
                for action in rule_actions:
                    action["rule_name"] = rule.name
                    action["response_time_s"] = rule.response_time_s
                actions.extend(rule_actions)
        return actions

    def _action_emergency_reorder(self, alert: dict) -> list[dict]:
        return [{
            "action_type": "emergency_reorder",
            "description": f"Emergency reorder triggered for alert: {alert.get('description', '')}",
            "priority": "critical",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }]

    def _action_lead_time_escalation(self, alert: dict) -> list[dict]:
        return [{
            "action_type": "escalation",
            "description": f"sigma_L violation: {alert.get('metric_value', 0):.2f} days > 1.5 day limit. "
                           "Escalating to supply chain manager.",
            "priority": "critical",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }, {
            "action_type": "safety_stock_increase",
            "description": "Temporarily increase safety stock multiplier by 1.5x",
            "priority": "high",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }]

    def _action_retrain_model(self, alert: dict) -> list[dict]:
        return [{
            "action_type": "model_retrain",
            "description": f"Bias drift detected ({alert.get('metric_value', 0):.1f}%). "
                           "Triggering automatic model retraining.",
            "priority": "medium",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }]

    def _action_last_time_buy(self, alert: dict) -> list[dict]:
        return [{
            "action_type": "last_time_buy",
            "description": "Component approaching EOL. Initiate LastTimeBuy procurement.",
            "priority": "high",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }]

