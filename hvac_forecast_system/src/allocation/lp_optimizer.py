"""
lp_optimizer.py
PuLP Linear Program for inventory allocation.

Decision variables: x[w, r] = units allocated from warehouse w to region r

Objective: minimize
  sum_{w,r} cost_per_unit[w,r] * x[w,r]            (logistics cost)
  + sum_w carrying_cost_rate * avg_inventory[w]     (carrying cost)

Constraints:
  1. Warehouse capacity: sum_r x[w,r] <= capacity[w]
  2. Demand satisfaction: sum_w x[w,r] >= P50_demand[r]
  3. Safety stock: inventory[w] - sum_r x[w,r] >= safety_stock[w]
  4. Inventory availability: sum_r x[w,r] <= current_inventory[w]
  5. SLA compliance: sum_w x[w,r] / demand[r] >= sla_target (0.95)
  6. Non-negativity: x[w,r] >= 0
"""

import pandas as pd
import numpy as np
from pulp import (LpProblem, LpMinimize, LpVariable, lpSum,
                  LpStatus, value, PULP_CBC_CMD)
from src.allocation.constraints import CARRYING_COST_RATE, SLA_TARGET


def run_allocation_optimizer(
    warehouses: pd.DataFrame,    # cols: warehouse_id, capacity, current_inventory, safety_stock
    regions: pd.DataFrame,       # cols: region, p50_demand, p90_demand
    cost_matrix: pd.DataFrame,   # cols: warehouse_id, region, cost_per_unit
) -> pd.DataFrame:
    """
    Solve LP. Returns allocation_plan DataFrame.
    Columns: [warehouse_id, region, allocated_units, cost]
    """
    prob = LpProblem("HVAC_Inventory_Allocation", LpMinimize)

    W = warehouses["warehouse_id"].tolist()
    R = regions["region"].tolist()

    # Decision variables
    x = {
        (w, r): LpVariable(f"x_{w}_{r}", lowBound=0, cat="Continuous")
        for w in W for r in R
    }

    # Cost lookup helpers
    cost_lookup    = cost_matrix.set_index(["warehouse_id", "region"])["cost_per_unit"].to_dict()
    cap_lookup     = warehouses.set_index("warehouse_id")["capacity"].to_dict()
    inv_lookup     = warehouses.set_index("warehouse_id")["current_inventory"].to_dict()
    ss_lookup      = warehouses.set_index("warehouse_id")["safety_stock"].to_dict()
    demand_lookup  = regions.set_index("region")["p50_demand"].to_dict()

    # Objective
    logistics_cost = lpSum(
        cost_lookup.get((w, r), 999999) * x[(w, r)]
        for w in W for r in R
    )
    carrying_cost = lpSum(
        CARRYING_COST_RATE * (inv_lookup[w] - lpSum(x[(w, r)] for r in R))
        for w in W
    )
    prob += logistics_cost + carrying_cost

    # Constraint 1: Warehouse capacity
    for w in W:
        prob += lpSum(x[(w, r)] for r in R) <= cap_lookup[w], f"cap_{w}"

    # Constraint 2: Demand satisfaction
    for r in R:
        prob += lpSum(x[(w, r)] for w in W) >= demand_lookup[r], f"demand_{r}"

    # Constraint 3: Safety stock preserved
    for w in W:
        prob += (inv_lookup[w] - lpSum(x[(w, r)] for r in R)) >= ss_lookup[w], f"ss_{w}"

    # Constraint 4: Inventory availability
    for w in W:
        prob += lpSum(x[(w, r)] for r in R) <= inv_lookup[w], f"avail_{w}"

    # Constraint 5: SLA compliance per region
    for r in R:
        prob += (
            lpSum(x[(w, r)] for w in W) >= SLA_TARGET * demand_lookup[r]
        ), f"sla_{r}"

    # Solve
    prob.solve(PULP_CBC_CMD(msg=0))

    status = LpStatus[prob.status]
    if status != "Optimal":
        raise RuntimeError(f"LP did not reach optimal solution. Status: {status}")

    # Extract results
    rows = []
    for w in W:
        for r in R:
            units = value(x[(w, r)]) or 0.0
            if units > 0.01:
                rows.append({
                    "warehouse_id":    w,
                    "region":          r,
                    "allocated_units": round(units),
                    "cost_per_unit":   cost_lookup.get((w, r), 0),
                    "total_cost_INR":  round(units * cost_lookup.get((w, r), 0)),
                })

    return pd.DataFrame(rows)
