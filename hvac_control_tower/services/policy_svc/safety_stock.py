"""
policy_svc/safety_stock.py
L4: Safety stock calculation per spec §4.4.

Formula (EXACT from spec):
  SS = Z x √(L_avg x sigma_D² + D_avg² x sigma_L²)

Where:
  Z = service-level z-score (default 1.65 for 95th percentile)
  L_avg = average lead time (days)
  sigma_D = standard deviation of daily demand
  D_avg = average daily demand
  sigma_L = standard deviation of lead time (days)

Property test requirements (spec §6.1):
  - Monotonicity in sigma_D: higher sigma_D → higher SS
  - Monotonicity in sigma_L: higher sigma_L → higher SS
  - Z=0 ⇒ SS=0
"""

import numpy as np
import pandas as pd
from services.policy_svc.constraints import (
    DEFAULT_Z, DEFAULT_LEAD_TIME_DAYS, LEAD_TIME_SIGMA_DEFAULT,
    MIN_SAFETY_BUFFER, SIGMA_L_MAX, FILL_RATE_CRITICAL
)
from contracts.events import AnomalyAlert, EventType
from datetime import datetime, timezone
import uuid


def compute_safety_stock(
    demand_avg: float,
    demand_std: float,
    lead_time_avg: float = DEFAULT_LEAD_TIME_DAYS,
    lead_time_std: float = LEAD_TIME_SIGMA_DEFAULT,
    z_score: float = DEFAULT_Z,
) -> float:
    """
    SS = Z x √(L_avg x sigma_D² + D_avg² x sigma_L²)
    Exactly as specified in §4.4.
    """
    if z_score == 0:
        return 0.0

    variance_component = (
        lead_time_avg * (demand_std ** 2)
        + (demand_avg ** 2) * (lead_time_std ** 2)
    )
    ss = z_score * np.sqrt(max(0, variance_component))
    return max(ss, MIN_SAFETY_BUFFER) if ss > 0 else 0.0


def compute_reorder_point(
    demand_avg: float,
    lead_time_avg: float = DEFAULT_LEAD_TIME_DAYS,
    safety_stock: float = 0.0,
) -> float:
    """ROP = D_avg x L_avg + SS"""
    return demand_avg * lead_time_avg + safety_stock


def check_lead_time_constraint(sigma_l: float) -> dict:
    """
    Spec §4.4: sigma_L <= 1.5 days.
    If violated, raise alert — do NOT silently absorb.
    """
    passed = sigma_l <= SIGMA_L_MAX
    result = {
        "sigma_l": round(sigma_l, 3),
        "threshold": SIGMA_L_MAX,
        "passed": passed,
    }

    if not passed:
        result["alert"] = AnomalyAlert(
            event_id=str(uuid.uuid4())[:12],
            timestamp=datetime.now(timezone.utc).isoformat(),
            event_type=EventType.ANOMALY_ALERT.value,
            source_service="policy-svc",
            severity="critical",
            metric_name="lead_time_variability",
            metric_value=sigma_l,
            threshold=SIGMA_L_MAX,
            description=f"sigma_L={sigma_l:.2f} days exceeds {SIGMA_L_MAX} day limit",
            recommended_action="Escalate to supply chain manager. Do NOT absorb silently.",
        )

    return result


def compute_safety_stock_batch(
    demand_df: pd.DataFrame,
    demand_col: str = "daily_demand_avg",
    demand_std_col: str = "daily_demand_std",
    lead_time_avg: float = DEFAULT_LEAD_TIME_DAYS,
    lead_time_std: float = LEAD_TIME_SIGMA_DEFAULT,
    z_score: float = DEFAULT_Z,
) -> pd.DataFrame:
    """Compute safety stock and reorder point for each row."""
    df = demand_df.copy()
    df["safety_stock"] = df.apply(
        lambda r: compute_safety_stock(
            r[demand_col], r[demand_std_col],
            lead_time_avg, lead_time_std, z_score
        ), axis=1
    )
    df["reorder_point"] = df.apply(
        lambda r: compute_reorder_point(
            r[demand_col], lead_time_avg, r["safety_stock"]
        ), axis=1
    )
    return df


