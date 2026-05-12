"""
policy_svc/constraints.py
L4: Inventory constraint definitions (spec §4.4).
"""

# Inventory targets enforced in optimizer constraints
INVENTORY_TURNOVER_MIN = 4.0    # x/yr
INVENTORY_TURNOVER_MAX = 6.0    # x/yr
CARRYING_COST_MIN = 0.18        # 18% annually
CARRYING_COST_MAX = 0.25        # 25% annually
CARRYING_COST_MONTHLY = 0.20 / 12  # ~1.67%/month (midpoint)

FILL_RATE_CRITICAL = 0.96       # ≥96% for critical parts
FILL_RATE_MISSION_CRITICAL = 0.98  # ≥98% for mission-critical equipment

SIGMA_L_MAX = 1.5               # days — if violated, raise alert
DEFAULT_Z = 1.65                # 95th percentile for safety stock
DEFAULT_LEAD_TIME_DAYS = 7.0
LEAD_TIME_SIGMA_DEFAULT = 1.2   # days (within <=1.5 constraint)

STOCKOUT_PENALTY_INR = 5000     # per unfulfilled unit
MIN_SAFETY_BUFFER = 50          # minimum safety stock units

# SKU classification
HERO_SKU_VOLUME_PERCENTILE = 80  # top 20% by volume = Hero SKUs

