"""
constraints.py
Constraint definitions for the LP allocation optimizer.
Loaded from configs/constraint_config.yaml when available,
otherwise uses defaults defined here.
"""

CARRYING_COST_RATE   = 0.02    # 2% of unit value per month
STOCKOUT_PENALTY     = 5000    # INR per unfulfilled unit
SLA_TARGET           = 0.95    # 95% fulfillment rate
LEAD_TIME_DAYS       = 7
MIN_DAYS_OF_SUPPLY   = 7
MAX_AGED_STOCK_RATIO = 0.30
MIN_SAFETY_BUFFER    = 50      # minimum safety stock units
