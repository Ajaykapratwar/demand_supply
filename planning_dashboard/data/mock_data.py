"""
mock_data.py
Synthetic data generators for all 9 dashboard views.
All values mimic realistic supply chain KPI ranges.
"""
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

rng = np.random.default_rng(42)

# ── Shared constants ──────────────────────────────────────────────────────────
REGIONS      = ["APAC", "EMEA", "NA", "LATAM"]
CATEGORIES   = ["Electronics", "Apparel", "FMCG", "Pharma", "Automotive"]
SKUS         = [f"SKU-{i:04d}" for i in range(1, 21)]
SUPPLIERS    = [f"SUP-{i:02d}" for i in range(1, 9)]
HORIZONS     = ["operational", "tactical", "strategic"]

def _dates(n: int, freq: str = "W") -> pd.DatetimeIndex:
    end = pd.Timestamp.today().normalize()
    return pd.date_range(end=end, periods=n, freq=freq)


# ── Executive KPIs ────────────────────────────────────────────────────────────
def get_executive_kpis() -> dict:
    return {
        "otif":            {"value": 93.4, "target": 95.0, "delta": +1.2,  "unit": "%",   "status": "warning"},
        "fill_rate":       {"value": 97.1, "target": 98.0, "delta": +0.3,  "unit": "%",   "status": "warning"},
        "mape":            {"value": 17.8, "target": 15.0, "delta": -2.1,  "unit": "%",   "status": "warning"},
        "stockout_rate":   {"value": 2.3,  "target": 1.0,  "delta": -0.4,  "unit": "%",   "status": "danger"},
        "dos":             {"value": 34.2, "target": 30.0, "delta": -3.1,  "unit": "days","status": "warning"},
        "inventory_cost":  {"value": 4.2,  "target": 4.0,  "delta": -0.15, "unit": "$M",  "status": "warning"},
        "total_revenue":   {"value": 128.4,"target": 130.0,"delta": +4.2,  "unit": "$M",  "status": "success"},
        "carbon_scope2":   {"value": 1840, "target": 1800, "delta": -60,   "unit": "tCO2","status": "warning"},
    }


def get_kpi_sparklines() -> dict:
    """7-week sparkline trend for each KPI."""
    weeks = 14
    return {
        "otif":          (92 + rng.normal(0, 0.5, weeks)).clip(89, 98).tolist(),
        "fill_rate":     (96.5 + rng.normal(0, 0.3, weeks)).clip(95, 99).tolist(),
        "mape":          (20 + rng.normal(0, 1, weeks)).clip(14, 26).tolist(),
        "stockout_rate": (3 + rng.normal(0, 0.2, weeks)).clip(1.5, 5).tolist(),
        "dos":           (36 + rng.normal(0, 1, weeks)).clip(28, 45).tolist(),
        "inventory_cost":(4.4 + rng.normal(0, 0.05, weeks)).clip(3.8, 5.2).tolist(),
        "total_revenue": (124 + rng.normal(0, 1.5, weeks)).clip(118, 132).tolist(),
        "carbon_scope2": (1900 + rng.normal(0, 20, weeks)).clip(1700, 2100).tolist(),
    }


# ── Plan vs Actual ────────────────────────────────────────────────────────────
def get_plan_vs_actual(weeks: int = 26) -> pd.DataFrame:
    dates = _dates(weeks)
    base = 5000 + np.cumsum(rng.normal(0, 50, weeks))
    return pd.DataFrame({
        "date":   dates,
        "plan":   base,
        "actual": base + rng.normal(0, 200, weeks),
        "p10":    base - rng.uniform(200, 400, weeks),
        "p90":    base + rng.uniform(200, 400, weeks),
    })


# ── Scenario Comparison ───────────────────────────────────────────────────────
SCENARIOS = [
    {"name": "Base Plan",          "cost_delta": 0,       "service_delta": 0,    "carbon_delta": 0,    "inventory_delta": 0},
    {"name": "Demand Surge +30%",  "cost_delta": 450000,  "service_delta": -2.1, "carbon_delta": 120,  "inventory_delta": 85000},
    {"name": "Supply Disruption",  "cost_delta": 780000,  "service_delta": -4.8, "carbon_delta": 200,  "inventory_delta": -30000},
    {"name": "Best Case",          "cost_delta": -120000, "service_delta": +1.5, "carbon_delta": -40,  "inventory_delta": 20000},
    {"name": "Sustainability Opt.","cost_delta": 95000,   "service_delta": -0.3, "carbon_delta": -320, "inventory_delta": 10000},
]

def get_scenarios() -> list:
    return SCENARIOS


# ── Supply-Demand Balance ─────────────────────────────────────────────────────
def get_supply_demand_balance() -> pd.DataFrame:
    weeks = 12
    dates = _dates(weeks)
    rows = []
    for region in REGIONS:
        demand = 1000 + rng.normal(0, 80, weeks)
        supply = demand * rng.uniform(0.88, 1.05, weeks)
        for i, d in enumerate(dates):
            gap = supply[i] - demand[i]
            rows.append({"date": d, "region": region,
                         "demand": demand[i], "supply": supply[i],
                         "gap": gap, "gap_pct": gap / demand[i] * 100})
    return pd.DataFrame(rows)


def get_inventory_dos_gauges() -> list:
    data = []
    for region in REGIONS:
        dos = rng.uniform(18, 55)
        target = 30
        risk = "danger" if dos < 20 else ("warning" if dos < 25 else "success")
        data.append({"region": region, "dos": round(dos, 1),
                     "target": target, "status": risk})
    return data


def get_action_queue() -> list:
    return [
        {"id": 1, "sku": "SKU-0003", "region": "APAC",  "issue": "Stockout risk (7 days)",    "priority": "CRITICAL", "action": "Expedite PO #4421"},
        {"id": 2, "sku": "SKU-0011", "region": "EMEA",  "issue": "Overstock 45 DOS",           "priority": "HIGH",     "action": "Redistribute to LATAM DC"},
        {"id": 3, "sku": "SKU-0007", "region": "NA",    "issue": "Supplier delay +10 days",    "priority": "HIGH",     "action": "Switch to SUP-03"},
        {"id": 4, "sku": "SKU-0015", "region": "LATAM", "issue": "Forecast bias >10%",         "priority": "MEDIUM",   "action": "Review promo plan"},
        {"id": 5, "sku": "SKU-0019", "region": "APAC",  "issue": "Lead time spike 3→8 weeks",  "priority": "MEDIUM",   "action": "Alert procurement"},
    ]


# ── Forecast Analytics ────────────────────────────────────────────────────────
def get_forecast_accuracy_kpis() -> dict:
    return {
        "mape":   {"value": 17.8, "target": 15.0, "delta": -2.1, "status": "warning"},
        "wape":   {"value": 12.4, "target": 12.0, "delta": -1.8, "status": "success"},
        "bias":   {"value": -2.3, "target": 0.0,  "delta": +0.8, "status": "success"},
        "fva":    {"value": 5.2,  "target": 3.0,  "delta": +1.1, "status": "success"},
        "p90_cov":{"value": 82.1, "target": 80.0, "delta": +3.2, "status": "success"},
    }


def get_forecast_vs_actual(weeks: int = 26) -> pd.DataFrame:
    dates = _dates(weeks)
    actual = 3000 + np.cumsum(rng.normal(0, 80, weeks))
    noise  = rng.normal(0, 180, weeks)
    return pd.DataFrame({
        "date":   dates,
        "actual": actual,
        "stat_forecast": actual + noise,
        "consensus":     actual + noise * 0.7,
        "p10": actual + noise - rng.uniform(300, 500, weeks),
        "p90": actual + noise + rng.uniform(300, 500, weeks),
    })


def get_fva_waterfall() -> list:
    """Steps: Naive → Statistical → Override → Consensus"""
    return [
        {"stage": "Naive Baseline",  "wape": 24.5, "delta":  0},
        {"stage": "Statistical",     "wape": 17.8, "delta": -6.7},
        {"stage": "Planner Override","wape": 16.2, "delta": -1.6},
        {"stage": "Consensus",       "wape": 12.4, "delta": -3.8},
    ]


def get_bias_by_category() -> pd.DataFrame:
    return pd.DataFrame({
        "category": CATEGORIES,
        "bias_pct": rng.uniform(-8, 8, len(CATEGORIES)).round(1),
        "mape":     rng.uniform(10, 30, len(CATEGORIES)).round(1),
    })


# ── Inventory Optimization ────────────────────────────────────────────────────
def get_inventory_geo_data() -> pd.DataFrame:
    coords = {
        "APAC":  (35.6, 139.7), "EMEA": (51.5, -0.1),
        "NA":    (40.7, -74.0), "LATAM":(-23.5, -46.6),
    }
    rows = []
    for region, (lat, lon) in coords.items():
        rows.append({
            "region": region, "lat": lat, "lon": lon,
            "stockout_prob": rng.uniform(0.02, 0.18),
            "dos": rng.uniform(18, 55),
            "inventory_value_m": rng.uniform(8, 32),
        })
    return pd.DataFrame(rows)


def get_service_vs_inventory_scatter() -> pd.DataFrame:
    n = 50
    safety_stock = rng.uniform(200, 3000, n)
    service_level = 85 + 13 * (1 - np.exp(-safety_stock / 1500)) + rng.normal(0, 0.5, n)
    return pd.DataFrame({
        "sku": rng.choice(SKUS, n),
        "safety_stock": safety_stock.round(0),
        "service_level": service_level.clip(85, 99.5).round(2),
        "category": rng.choice(CATEGORIES, n),
    })


def get_safety_stock_simulation(service_level: float = 0.95) -> dict:
    """Given service_level, compute safety stock impact."""
    from scipy.stats import norm
    z = norm.ppf(service_level)
    demand_std = 250
    lt_mean = 7
    lt_std = 1.5
    demand_mean = 1000
    ss = z * np.sqrt(lt_mean * demand_std**2 + demand_mean**2 * lt_std**2)
    rop = demand_mean * lt_mean + ss
    wc_impact = ss * 12.5  # unit cost proxy
    return {
        "service_level": round(service_level * 100, 1),
        "safety_stock": round(ss, 0),
        "reorder_point": round(rop, 0),
        "working_capital_usd": round(wc_impact, 0),
        "stockout_prob": round((1 - service_level) * 100, 2),
    }


# ── Capacity Planning ─────────────────────────────────────────────────────────
def get_capacity_utilization() -> list:
    plants = ["Plant-A (Shanghai)", "Plant-B (Frankfurt)", "Plant-C (Chicago)", "Plant-D (São Paulo)"]
    return [
        {"plant": p,
         "utilization": round(rng.uniform(0.65, 0.98), 3),
         "capacity": int(rng.uniform(10000, 30000)),
         "oee": round(rng.uniform(0.72, 0.91), 3)}
        for p in plants
    ]


def get_capacity_load_profile(weeks: int = 12) -> pd.DataFrame:
    dates = _dates(weeks)
    rows = []
    for plant in ["Plant-A", "Plant-B", "Plant-C", "Plant-D"]:
        load = rng.uniform(0.65, 1.0, weeks)
        for i, d in enumerate(dates):
            rows.append({"date": d, "plant": plant, "utilization": round(load[i], 3)})
    return pd.DataFrame(rows)


# ── Financial Impact ──────────────────────────────────────────────────────────
def get_financial_kpis() -> dict:
    return {
        "revenue":        {"value": 128.4, "target": 130.0, "delta": +4.2,  "unit": "$M"},
        "gross_margin":   {"value": 34.2,  "target": 35.0,  "delta": +0.8,  "unit": "%"},
        "inventory_cost": {"value": 4.2,   "target": 4.0,   "delta": -0.15, "unit": "$M"},
        "logistics_cost": {"value": 8.7,   "target": 8.2,   "delta": +0.5,  "unit": "$M"},
        "expediting_cost":{"value": 0.95,  "target": 0.5,   "delta": -0.2,  "unit": "$M"},
    }


def get_pl_bridge_waterfall() -> list:
    return [
        {"label": "Budget",          "value": 130.0, "type": "total"},
        {"label": "Volume Effect",   "value":  -1.8, "type": "negative"},
        {"label": "Price Effect",    "value":  +2.1, "type": "positive"},
        {"label": "Mix Effect",      "value":  -0.9, "type": "negative"},
        {"label": "Logistics Var.",  "value":  -0.5, "type": "negative"},
        {"label": "Promo Impact",    "value":  -0.5, "type": "negative"},
        {"label": "Forecast",        "value": 128.4, "type": "total"},
    ]


def get_budget_vs_forecast(months: int = 12) -> pd.DataFrame:
    dates = pd.date_range(start="2025-01", periods=months, freq="MS")
    budget = 10.0 + rng.normal(0, 0.5, months)
    forecast = budget + rng.normal(0, 0.8, months)
    return pd.DataFrame({"month": dates, "budget": budget.round(2),
                         "forecast": forecast.round(2)})


# ── Risk Monitoring ───────────────────────────────────────────────────────────
def get_risk_scores() -> pd.DataFrame:
    rows = []
    for supplier in SUPPLIERS:
        rows.append({
            "supplier": supplier,
            "risk_score": round(rng.uniform(0.1, 0.95), 2),
            "reliability": round(rng.uniform(0.70, 0.99), 2),
            "lead_time_cv": round(rng.uniform(0.05, 0.45), 2),
            "on_time_rate": round(rng.uniform(0.72, 0.99), 2),
            "risk_category": rng.choice(["low", "medium", "high", "critical"],
                                        p=[0.3, 0.4, 0.2, 0.1]),
        })
    return pd.DataFrame(rows)


def get_risk_matrix() -> pd.DataFrame:
    risks = [
        {"risk": "Supplier Concentration", "probability": 0.7, "impact": 0.9, "category": "Supply"},
        {"risk": "Port Disruption",        "probability": 0.4, "impact": 0.8, "category": "Logistics"},
        {"risk": "Demand Spike +40%",      "probability": 0.5, "impact": 0.6, "category": "Demand"},
        {"risk": "Currency Volatility",    "probability": 0.6, "impact": 0.4, "category": "Financial"},
        {"risk": "Regulatory Change",      "probability": 0.3, "impact": 0.7, "category": "Compliance"},
        {"risk": "Quality Defect Rate",    "probability": 0.25,"impact": 0.5, "category": "Quality"},
        {"risk": "IT System Failure",      "probability": 0.2, "impact": 0.8, "category": "Operational"},
    ]
    return pd.DataFrame(risks)


def get_mitigation_actions() -> list:
    return [
        {"risk": "Supplier Concentration", "action": "Dual-source SUP-01 with SUP-05", "owner": "Procurement", "due": "2025-07-01", "status": "In Progress"},
        {"risk": "Port Disruption",        "action": "Pre-position 15 DOS buffer at inland DC", "owner": "Logistics", "due": "2025-06-15", "status": "Planned"},
        {"risk": "Demand Spike",           "action": "Activate flex capacity contract with Plant-B", "owner": "Operations", "due": "2025-08-01", "status": "Approved"},
    ]


# ── Sustainability ────────────────────────────────────────────────────────────
def get_sustainability_kpis() -> dict:
    return {
        "scope1": {"value": 420,  "target": 400,  "delta": -15,  "unit": "tCO2e"},
        "scope2": {"value": 1840, "target": 1800, "delta": -60,  "unit": "tCO2e"},
        "scope3": {"value": 8200, "target": 8000, "delta": -180, "unit": "tCO2e"},
        "carbon_intensity": {"value": 0.32, "target": 0.30, "delta": -0.02, "unit": "kg/unit"},
        "renewable_pct":    {"value": 42.0, "target": 50.0, "delta": +5.0,  "unit": "%"},
    }


def get_emissions_breakdown() -> list:
    return [
        {"source": "Transportation",  "tco2e": 3200},
        {"source": "Manufacturing",   "tco2e": 2800},
        {"source": "Warehousing",     "tco2e": 1840},
        {"source": "Packaging",       "tco2e": 820},
        {"source": "Last Mile",       "tco2e": 420},
        {"source": "Other",           "tco2e": 380},
    ]


def get_pareto_scatter() -> pd.DataFrame:
    n = 30
    cost_delta = rng.uniform(-200, 800, n)
    carbon_delta = -cost_delta * rng.uniform(0.3, 0.6, n) + rng.normal(0, 50, n)
    return pd.DataFrame({
        "scenario": [f"Scenario-{i}" for i in range(n)],
        "cost_delta_k": cost_delta.round(0),
        "carbon_delta": carbon_delta.round(0),
        "service_delta": rng.uniform(-3, 3, n).round(1),
    })


# ── Regional Planning ─────────────────────────────────────────────────────────
def get_regional_kpis() -> pd.DataFrame:
    rows = []
    for region in REGIONS:
        rows.append({
            "region": region,
            "revenue_m": round(rng.uniform(20, 45), 1),
            "otif": round(rng.uniform(89, 97), 1),
            "fill_rate": round(rng.uniform(93, 99), 1),
            "dos": round(rng.uniform(22, 48), 1),
            "stockout_pct": round(rng.uniform(0.5, 4.5), 1),
            "plan_attainment": round(rng.uniform(88, 102), 1),
        })
    return pd.DataFrame(rows)


def get_region_vs_plan(weeks: int = 8) -> pd.DataFrame:
    rows = []
    dates = _dates(weeks)
    for region in REGIONS:
        plan = rng.uniform(800, 1500, weeks)
        actual = plan * rng.uniform(0.88, 1.06, weeks)
        for i, d in enumerate(dates):
            rows.append({"date": d, "region": region,
                         "plan": plan[i].round(0), "actual": actual[i].round(0)})
    return pd.DataFrame(rows)
