"""
twin_svc/equipment.py
L2: Equipment performance models and BOM health monitoring.
Models thermodynamic curves for chiller, AHU, RTU equipment classes.
Flags end-of-life components (EOL <= 12 months → LastTimeBuy event).
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass
from typing import Optional


@dataclass
class EquipmentProfile:
    """Performance curve parameters for one equipment class."""
    equipment_type: str
    rated_capacity_kw: float
    cop_nominal: float          # Coefficient of Performance at rated conditions
    lifespan_years: float
    maintenance_interval_hours: float
    failure_rate_per_1000h: float   # baseline failure rate


# Default profiles per equipment class (spec §4.2)
EQUIPMENT_PROFILES = {
    "chiller": EquipmentProfile("chiller", 350.0, 5.5, 20.0, 4000, 0.8),
    "ahu": EquipmentProfile("ahu", 50.0, 3.8, 15.0, 3000, 1.2),
    "rtu": EquipmentProfile("rtu", 75.0, 3.2, 15.0, 3000, 1.5),
    "split_ac": EquipmentProfile("split_ac", 5.0, 3.5, 10.0, 2000, 2.0),
    "window_ac": EquipmentProfile("window_ac", 3.0, 2.8, 8.0, 2000, 2.5),
    "portable": EquipmentProfile("portable", 2.0, 2.5, 5.0, 1500, 3.0),
    "tower": EquipmentProfile("tower", 4.0, 3.0, 8.0, 2000, 2.2),
}


def compute_degraded_cop(profile: EquipmentProfile, age_years: float,
                         ambient_temp_c: float = 35.0) -> float:
    """
    Thermodynamic performance curve: COP degrades with age and ambient temp.
    COP_actual = COP_nominal x age_factor x temp_factor
    """
    # Age degradation: linear 2% per year
    age_factor = max(0.3, 1.0 - 0.02 * age_years)

    # Temperature penalty: COP drops ~3% per degree above 35°C
    temp_delta = max(0, ambient_temp_c - 35.0)
    temp_factor = max(0.5, 1.0 - 0.03 * temp_delta)

    return round(profile.cop_nominal * age_factor * temp_factor, 3)


def compute_failure_probability(profile: EquipmentProfile, age_years: float,
                                runtime_hours: float) -> float:
    """
    Weibull-inspired failure probability.
    Increases with age and runtime beyond maintenance interval.
    """
    age_factor = (age_years / profile.lifespan_years) ** 2
    overdue_factor = max(0, runtime_hours % profile.maintenance_interval_hours
                         - profile.maintenance_interval_hours * 0.8) / 1000
    base_rate = profile.failure_rate_per_1000h / 1000

    prob = min(1.0, base_rate * (1 + age_factor + overdue_factor))
    return round(prob, 4)


def check_eol_status(age_years: float, lifespan_years: float,
                     eol_threshold_months: int = 12) -> dict:
    """
    Check if equipment is approaching end-of-life.
    EOL <= 12 months → emit LastTimeBuy event (spec §4.2).
    """
    remaining_years = max(0, lifespan_years - age_years)
    remaining_months = remaining_years * 12

    return {
        "remaining_months": round(remaining_months, 1),
        "is_eol": remaining_months <= eol_threshold_months,
        "last_time_buy": remaining_months <= eol_threshold_months,
        "urgency": "critical" if remaining_months <= 3 else
                   "warning" if remaining_months <= eol_threshold_months else "normal",
    }


def generate_equipment_fleet(n_units: int = 500, seed: int = 42) -> pd.DataFrame:
    """Generate synthetic equipment fleet for simulation."""
    rng = np.random.RandomState(seed)
    types = list(EQUIPMENT_PROFILES.keys())
    regions = ["North", "South", "East", "West"]

    records = []
    for i in range(n_units):
        eq_type = rng.choice(types)
        profile = EQUIPMENT_PROFILES[eq_type]
        age = round(rng.uniform(0, profile.lifespan_years * 1.1), 1)
        runtime = round(age * rng.uniform(1500, 3500), 0)

        records.append({
            "equipment_id": f"EQ-{i:04d}",
            "equipment_type": eq_type,
            "region": rng.choice(regions),
            "site_id": f"SITE-{rng.randint(1, 100):03d}",
            "age_years": age,
            "runtime_hours": runtime,
            "cop_actual": compute_degraded_cop(profile, age),
            "failure_prob": compute_failure_probability(profile, age, runtime),
            **check_eol_status(age, profile.lifespan_years),
        })
    return pd.DataFrame(records)

