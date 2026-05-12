"""
twin_svc/scenario.py
L2: Scenario simulation engine (spec §4.2, §6.5).
Implements the four canonical scenarios:
  1. Early September freeze
  2. Copper +10% spot-price shock
  3. SEER2 transition cliff
  4. Tier-1 supplier outage

Each scenario takes inputs and produces inventory/fill-rate trajectories.
Verification: copper +10% must complete in <30s (spec §4.2).
"""

import numpy as np
import pandas as pd
import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScenarioInput:
    """Inputs to a scenario simulation."""
    name: str
    horizon_days: int = 90
    parameters: dict = field(default_factory=dict)


@dataclass
class ScenarioOutput:
    """Outputs from a scenario simulation."""
    name: str
    cost_delta_pct: float
    fill_rate_trajectory: list
    inventory_trajectory: list
    recommended_actions: list
    simulation_time_s: float


class ScenarioEngine:
    """Runs what-if scenarios against inventory/demand baselines."""

    def __init__(self, baseline_demand: pd.Series = None,
                 baseline_inventory: float = 10000,
                 baseline_cost_per_unit: float = 500.0,
                 daily_consumption_rate: float = 100.0):
        self.baseline_demand = baseline_demand
        self.baseline_inventory = baseline_inventory
        self.baseline_cost = baseline_cost_per_unit
        self.daily_rate = daily_consumption_rate

    def run_scenario(self, scenario: ScenarioInput) -> ScenarioOutput:
        dispatch = {
            "copper_shock": self._copper_shock,
            "early_freeze": self._early_freeze,
            "seer2_transition": self._seer2_transition,
            "supplier_outage": self._supplier_outage,
        }
        handler = dispatch.get(scenario.name)
        if handler is None:
            raise ValueError(f"Unknown scenario: {scenario.name}. "
                             f"Available: {list(dispatch.keys())}")
        return handler(scenario)

    def _copper_shock(self, scenario: ScenarioInput) -> ScenarioOutput:
        """Scenario 2: Copper +X% spot-price shock."""
        start = time.time()
        price_delta_pct = scenario.parameters.get("price_delta_pct", 10.0)
        horizon = scenario.horizon_days

        # Simulate day-by-day inventory and cost
        inventory = self.baseline_inventory
        inv_trajectory = []
        fill_trajectory = []
        total_cost_delta = 0

        for day in range(horizon):
            demand = self.daily_rate * (1 + np.random.normal(0, 0.05))
            # Cost increases proportionally to copper content (~30% of unit cost)
            copper_fraction = 0.30
            cost_increase = self.baseline_cost * copper_fraction * (price_delta_pct / 100)
            total_cost_delta += cost_increase * min(demand, inventory)

            inventory = max(0, inventory - demand)
            # Replenishment every 7 days
            if day % 7 == 6:
                inventory += self.daily_rate * 7 * 0.9

            inv_trajectory.append(round(inventory))
            fill_rate = min(1.0, inventory / max(demand, 1))
            fill_trajectory.append(round(fill_rate, 3))

        cost_delta_pct = (total_cost_delta / (self.baseline_cost * self.daily_rate * horizon)) * 100
        elapsed = time.time() - start

        actions = [
            f"Pre-buy copper-intensive components before price fully propagates",
            f"Shift orders to aluminum-based alternatives where specs allow",
            f"Expected cost increase: {cost_delta_pct:.1f}% over {horizon} days",
        ]

        return ScenarioOutput(
            name="copper_shock",
            cost_delta_pct=round(cost_delta_pct, 2),
            fill_rate_trajectory=fill_trajectory,
            inventory_trajectory=inv_trajectory,
            recommended_actions=actions,
            simulation_time_s=round(elapsed, 3),
        )

    def _early_freeze(self, scenario: ScenarioInput) -> ScenarioOutput:
        """Scenario 1: Early September freeze — heating demand surge."""
        start = time.time()
        demand_surge_pct = scenario.parameters.get("demand_surge_pct", 40.0)
        horizon = scenario.horizon_days

        inventory = self.baseline_inventory
        inv_trajectory = []
        fill_trajectory = []

        for day in range(horizon):
            # Surge starts at day 14 (2 weeks early)
            surge = 1.0 + (demand_surge_pct / 100) if day >= 14 else 1.0
            demand = self.daily_rate * surge * (1 + np.random.normal(0, 0.03))

            inventory = max(0, inventory - demand)
            if day % 7 == 6:
                inventory += self.daily_rate * 7 * 0.85

            inv_trajectory.append(round(inventory))
            fill_trajectory.append(round(min(1.0, inventory / max(demand, 1)), 3))

        elapsed = time.time() - start

        return ScenarioOutput(
            name="early_freeze",
            cost_delta_pct=round(demand_surge_pct * 0.6, 2),
            fill_rate_trajectory=fill_trajectory,
            inventory_trajectory=inv_trajectory,
            recommended_actions=[
                "Pre-position furnaces to northern DCs within 48 hours",
                f"Increase safety stock by {demand_surge_pct:.0f}% for heating SKUs",
                "Activate emergency supplier contracts",
            ],
            simulation_time_s=round(elapsed, 3),
        )

    def _seer2_transition(self, scenario: ScenarioInput) -> ScenarioOutput:
        """Scenario 3: SEER2 transition cliff — 30% catalog obsolescence."""
        start = time.time()
        obsolescence_pct = scenario.parameters.get("obsolescence_pct", 30.0)
        transition_days = scenario.parameters.get("transition_days", 60)
        horizon = scenario.horizon_days

        inventory = self.baseline_inventory
        inv_trajectory = []
        fill_trajectory = []

        for day in range(horizon):
            if day < transition_days:
                # Demand shifts: obsolete SKUs drop, new SKUs ramp
                ramp = day / transition_days
                effective_demand = self.daily_rate * (1 - obsolescence_pct / 100 * (1 - ramp))
            else:
                effective_demand = self.daily_rate

            demand = effective_demand * (1 + np.random.normal(0, 0.04))
            inventory = max(0, inventory - demand)
            if day % 7 == 6:
                inventory += self.daily_rate * 7 * 0.8

            inv_trajectory.append(round(inventory))
            fill_trajectory.append(round(min(1.0, inventory / max(demand, 1)), 3))

        elapsed = time.time() - start

        return ScenarioOutput(
            name="seer2_transition",
            cost_delta_pct=round(obsolescence_pct * 0.8, 2),
            fill_rate_trajectory=fill_trajectory,
            inventory_trajectory=inv_trajectory,
            recommended_actions=[
                f"Initiate LastTimeBuy for {obsolescence_pct:.0f}% of catalog within 30 days",
                "Accelerate SEER2-compliant SKU onboarding",
                "Markdown obsolete inventory to reduce carrying cost",
            ],
            simulation_time_s=round(elapsed, 3),
        )

    def _supplier_outage(self, scenario: ScenarioInput) -> ScenarioOutput:
        """Scenario 4: Tier-1 supplier outage — sigma_L doubles for 30 days."""
        start = time.time()
        outage_days = scenario.parameters.get("outage_days", 30)
        sigma_l_multiplier = scenario.parameters.get("sigma_l_multiplier", 2.0)
        horizon = scenario.horizon_days

        inventory = self.baseline_inventory
        inv_trajectory = []
        fill_trajectory = []
        base_lead_time = 7  # days

        for day in range(horizon):
            demand = self.daily_rate * (1 + np.random.normal(0, 0.05))
            inventory = max(0, inventory - demand)

            # Replenishment with variable lead time
            if day % 7 == 6:
                if day < outage_days:
                    lead_time_var = base_lead_time * sigma_l_multiplier
                    replenish_factor = max(0.3, 1.0 - (lead_time_var - base_lead_time) / 20)
                else:
                    replenish_factor = 0.9
                inventory += self.daily_rate * 7 * replenish_factor

            inv_trajectory.append(round(inventory))
            fill_trajectory.append(round(min(1.0, inventory / max(demand, 1)), 3))

        elapsed = time.time() - start

        return ScenarioOutput(
            name="supplier_outage",
            cost_delta_pct=round(15.0 * sigma_l_multiplier, 2),
            fill_rate_trajectory=fill_trajectory,
            inventory_trajectory=inv_trajectory,
            recommended_actions=[
                "Activate secondary supplier contracts immediately",
                f"Increase safety stock by {sigma_l_multiplier:.0f}x for affected SKUs",
                "Alert: sigma_L exceeds 1.5 day threshold — do NOT silently absorb",
                "Re-route shipments through alternative logistics channels",
            ],
            simulation_time_s=round(elapsed, 3),
        )

