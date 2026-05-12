"""
sensing_svc/connectors.py
L1: Data source connectors — loads raw CSV datasets and emits typed events.
Connectors: Order history, Sales, Demand signals, Warehouse, Logistics.
Simulates IoT telemetry and NOAA weather polling.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timezone
import uuid


def _eid() -> str:
    return str(uuid.uuid4())[:12]


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_orders(path: str) -> pd.DataFrame:
    """Load dataset1_order_history.csv with date parsing."""
    df = pd.read_csv(path, parse_dates=["Date"])
    df["YearMonth"] = df["Date"].dt.to_period("M")
    return df


def load_sales(path: str) -> pd.DataFrame:
    """Load dataset2_sales_revenue.csv — contains demand target."""
    df = pd.read_csv(path, parse_dates=["Date"])
    df["YearMonth"] = df["Date"].dt.to_period("M")
    return df


def load_signals(path: str) -> pd.DataFrame:
    """Load dataset3_demand_signals.csv — weather/macro features."""
    df = pd.read_csv(path, parse_dates=["Date"])
    df["YearMonth"] = df["Date"].dt.to_period("M")
    # Drop near-zero-variance columns
    drop = ["COVID_Impact_Score", "Semiconductor_Shortage_Score", "Consumer_Confidence_Index"]
    df = df.drop(columns=[c for c in drop if c in df.columns])
    return df


def load_warehouse(path: str) -> pd.DataFrame:
    """Load dataset4_warehouse_capacity.csv — supply-side signals."""
    df = pd.read_csv(path, parse_dates=["Date"])
    df["YearMonth"] = df["Date"].dt.to_period("M")
    return df


def load_logistics(path: str) -> pd.DataFrame:
    """Load dataset5_logistics_cost.csv — shipping cost signals."""
    df = pd.read_csv(path, parse_dates=["Date"])
    df["YearMonth"] = df["Date"].dt.to_period("M")
    return df


def generate_synthetic_telemetry(n_events: int = 1000, seed: int = 42) -> pd.DataFrame:
    """
    Generate synthetic IoT telemetry for v1 (no real hardware).
    Simulates chiller/AHU/RTU sensor readings.
    """
    rng = np.random.RandomState(seed)
    equipment_types = ["chiller", "ahu", "rtu", "split_ac"]
    regions = ["North", "South", "East", "West"]

    records = []
    for i in range(n_events):
        eq_type = rng.choice(equipment_types)
        base_temp = {"chiller": 7, "ahu": 22, "rtu": 25, "split_ac": 24}[eq_type]
        records.append({
            "event_id": f"TEL-{i:06d}",
            "timestamp": _ts(),
            "equipment_id": f"EQ-{rng.randint(1, 200):04d}",
            "equipment_type": eq_type,
            "region": rng.choice(regions),
            "temperature_c": round(base_temp + rng.normal(0, 2), 2),
            "pressure_kpa": round(rng.uniform(200, 400), 2),
            "vibration_mm_s": round(rng.exponential(1.5), 3),
            "refrigerant_level_pct": round(rng.uniform(70, 100), 1),
            "power_kw": round(rng.uniform(1, 50), 2),
            "runtime_hours": round(rng.uniform(100, 20000), 0),
        })
    return pd.DataFrame(records)

