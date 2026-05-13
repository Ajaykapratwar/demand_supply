# data/mock_data.py — Realistic synthetic data for all 9 dashboards
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _weeks(n=52):
    return pd.date_range("2024-01-01", periods=n, freq="W-MON")


def _months(n=24):
    return pd.date_range("2024-01-01", periods=n, freq="MS")


# ─── Executive Summary ────────────────────────────────────────────────────────

def executive_kpis():
    return [
        {"title": "OTIF",           "value": "94.1%", "target": "95%", "delta": "+0.8%",  "trend": rng.uniform(91, 96, 14).tolist(),  "status": "warning"},
        {"title": "Fill Rate",      "value": "97.3%", "target": "98%", "delta": "+0.3%",  "trend": rng.uniform(95, 99, 14).tolist(),  "status": "warning"},
        {"title": "Stockout Rate",  "value": "3.2%",  "target": "<2%", "delta": "-0.5%",  "trend": rng.uniform(2, 5, 14).tolist(),    "status": "danger"},
        {"title": "MAPE",           "value": "18.4%", "target": "<20%","delta": "-1.2%",  "trend": rng.uniform(16, 24, 14).tolist(),  "status": "success"},
        {"title": "Inventory DOS",  "value": "38d",   "target": "35d", "delta": "+3d",    "trend": rng.uniform(32, 45, 14).tolist(),  "status": "warning"},
        {"title": "Total Cost ($M)","value": "$45.2", "target": "$44M","delta": "+$1.2M", "trend": rng.uniform(42, 48, 14).tolist(),  "status": "warning"},
        {"title": "Total Revenue",  "value": "$128.4M","target": "$130M","delta": "+$4.2M", "trend": rng.uniform(118, 132, 14).tolist(),  "status": "success"},
        {"title": "Carbon Scope 2", "value": "1,840t", "target": "1,800t","delta": "-60t",   "trend": rng.uniform(1700, 2100, 14).tolist(),"status": "warning"},
    ]


def plan_vs_actual():
    weeks = _weeks(26)
    plan   = 1000 + np.cumsum(rng.normal(0, 30, 26))
    actual = plan * rng.uniform(0.93, 1.07, 26)
    return pd.DataFrame({"week": weeks, "plan": plan, "actual": actual})


def scenario_comparison():
    return pd.DataFrame({
        "Scenario":          ["Base Plan", "Demand Surge +20%", "Supply Disruption", "Sustainability"],
        "Total Cost ($M)":   [45.2,         52.1,                 49.8,                46.1],
        "Service Level (%)": [94.1,         91.3,                 88.7,                93.8],
        "Carbon (tCO₂e)":    [1200,         1380,                 1250,                980],
        "Inventory ($M)":    [18.4,         22.1,                 19.8,                17.9],
    })


def risk_strip():
    return [
        {"supplier": "Supplier A (APAC)", "risk": "HIGH",   "score": 0.82, "issue": "Lead time +15d"},
        {"supplier": "Supplier B (EMEA)", "risk": "MEDIUM", "score": 0.55, "issue": "Quality defect 4.2%"},
        {"supplier": "Supplier C (US)",   "risk": "LOW",    "score": 0.21, "issue": "On-track"},
    ]


# ─── Operational Planning ─────────────────────────────────────────────────────

def supply_demand_balance():
    skus = [f"SKU-{i:03d}" for i in range(1, 13)]
    weeks = [f"Wk{i}" for i in range(1, 9)]
    data = rng.uniform(-30, 50, (12, 8))          # + = surplus, - = stockout risk
    return pd.DataFrame(data, index=skus, columns=weeks)


def inventory_dos():
    locations = ["DC-APAC", "DC-EMEA", "DC-US", "Plant-MX", "Plant-DE"]
    return pd.DataFrame({
        "location": locations,
        "dos_current": rng.uniform(20, 55, 5).round(1),
        "dos_target":  [35, 35, 35, 28, 28],
        "status": ["warning", "success", "danger", "success", "warning"],
    })


def action_queue():
    return pd.DataFrame({
        "Priority": ["P1", "P1", "P2", "P2", "P3"],
        "Action":   [
            "Expedite PO-4821 (Supplier A) — 5,000 units at risk",
            "Raise reorder for SKU-047 (DC-APAC) — DOS=12d",
            "Review promo uplift SKU-112 — forecast bias +18%",
            "Transfer 2,000 units DC-EMEA → DC-US (imbalance)",
            "Update lead time Supplier C — actual 21d vs 14d planned",
        ],
        "Owner":    ["SC Manager", "Demand Planner", "Demand Planner", "SC Manager", "Procurement"],
        "Due":      ["Today", "Today", "Fri", "Mon", "Mon"],
    })


# ─── Forecast Analytics ───────────────────────────────────────────────────────

def forecast_accuracy_kpis():
    return [
        {"title": "MAPE",       "value": "18.4%", "target": "<20%", "delta": "-1.2pp", "trend": rng.uniform(16, 24, 14).tolist(), "status": "success"},
        {"title": "WAPE",       "value": "14.1%", "target": "<15%", "delta": "-0.8pp", "trend": rng.uniform(12, 18, 14).tolist(), "status": "success"},
        {"title": "Bias",       "value": "+2.3%", "target": "±5%",  "delta": "-0.4pp", "trend": rng.uniform(-5, 5, 14).tolist(),  "status": "success"},
        {"title": "FVA",        "value": "+3.1pp","target": ">0",   "delta": "+0.6pp", "trend": rng.uniform(0, 5, 14).tolist(),   "status": "success"},
        {"title": "Override Rate","value":"14.2%","target": "<20%", "delta": "-2.1pp", "trend": rng.uniform(10, 22, 14).tolist(), "status": "success"},
        {"title": "P90 Coverage","value":"79.4%", "target": "~80%", "delta": "-0.6pp", "trend": rng.uniform(74, 85, 14).tolist(), "status": "warning"},
    ]


def forecast_fan_chart():
    weeks = _weeks(26)
    mean = 1000 + np.cumsum(rng.normal(0, 20, 26))
    spread = np.linspace(20, 120, 26)
    actual = mean[:13] * rng.uniform(0.94, 1.06, 13)
    return pd.DataFrame({
        "week":      weeks,
        "p10":       mean - 1.28 * spread,
        "p50":       mean,
        "p90":       mean + 1.28 * spread,
        "actual":    list(actual) + [None] * 13,
    })


def fva_waterfall():
    return pd.DataFrame({
        "stage": ["Naïve Baseline", "Statistical Model", "External Signals", "Planner Overrides", "Final Consensus"],
        "wape":  [28.3, 22.1, 19.8, 18.9, 18.4],
    })


# ─── Inventory Optimization ───────────────────────────────────────────────────

def inventory_geo():
    return pd.DataFrame({
        "location":    ["Singapore", "Frankfurt", "Dallas", "Mumbai", "São Paulo"],
        "lat":         [1.35, 50.11, 32.78, 19.08, -23.55],
        "lon":         [103.82, 8.68, -96.80, 72.88, -46.63],
        "dos":         [42, 38, 28, 55, 33],
        "stock_value": [8.2, 6.1, 5.8, 4.3, 3.7],
        "status":      ["warning", "success", "danger", "warning", "success"],
    })


def service_vs_inventory():
    n = 60
    return pd.DataFrame({
        "sku":         [f"SKU-{i:03d}" for i in range(n)],
        "service_lvl": rng.uniform(82, 99.5, n).round(1),
        "inv_value":   rng.uniform(0.2, 4.5, n).round(2),
        "abc":         rng.choice(["A", "B", "C"], n, p=[0.2, 0.3, 0.5]),
    })


def safety_stock_sim(service_level=0.95):
    z = {0.85: 1.04, 0.90: 1.28, 0.95: 1.65, 0.98: 2.05, 0.99: 2.33}
    z_val = z.get(round(service_level, 2), 1.65)
    demand_std, lt_mean, lt_std = 45, 14, 3
    ss = z_val * np.sqrt(lt_mean * demand_std**2 + 900 * lt_std**2)
    return {"safety_stock_units": int(ss), "working_capital_usd": int(ss * 12.5),
            "stockout_prob": round(1 - service_level, 3)}


# ─── Capacity Planning ────────────────────────────────────────────────────────

def capacity_utilization():
    plants = ["Plant-MX", "Plant-DE", "Plant-CN", "Plant-IN"]
    return pd.DataFrame({
        "plant":       plants,
        "utilization": rng.uniform(62, 97, 4).round(1),
        "capacity":    [5000, 4200, 6800, 3500],
        "planned":     rng.uniform(3500, 6500, 4).round(0),
    })


def load_profile():
    weeks = [f"Wk{i}" for i in range(1, 13)]
    plants = ["Plant-MX", "Plant-DE", "Plant-CN"]
    data = {p: rng.uniform(60, 105, 12).round(1) for p in plants}
    df = pd.DataFrame(data, index=weeks)
    df.index.name = "week"
    return df.reset_index()


def gantt_data():
    return pd.DataFrame({
        "task":   ["Production Run A", "Maintenance", "Production Run B", "Changeover", "Production Run C"],
        "start":  ["2024-06-03", "2024-06-10", "2024-06-12", "2024-06-19", "2024-06-21"],
        "finish": ["2024-06-10", "2024-06-12", "2024-06-19", "2024-06-21", "2024-06-28"],
        "plant":  ["Plant-MX", "Plant-MX", "Plant-DE", "Plant-DE", "Plant-CN"],
    })


# ─── Financial Impact ─────────────────────────────────────────────────────────

def financial_kpis():
    return [
        {"title": "Revenue ($M)",   "value": "$284.1","target": "$290M", "delta": "-$5.9M",  "trend": rng.uniform(270, 295, 14).tolist(), "status": "warning"},
        {"title": "Gross Margin %", "value": "38.2%", "target": "39%",   "delta": "-0.8pp",  "trend": rng.uniform(36, 41, 14).tolist(),   "status": "warning"},
        {"title": "COGS ($M)",      "value": "$175.3","target": "$173M", "delta": "+$2.3M",  "trend": rng.uniform(168, 182, 14).tolist(), "status": "danger"},
        {"title": "Expediting ($M)","value": "$3.2",  "target": "<$2M",  "delta": "+$1.2M",  "trend": rng.uniform(1.5, 4.5, 14).tolist(), "status": "danger"},
        {"title": "Budget Variance","value": "-2.1%", "target": "±1%",   "delta": "-0.3pp",  "trend": rng.uniform(-4, 2, 14).tolist(),    "status": "danger"},
        {"title": "EVA ($M)",       "value": "$12.4", "target": "$15M",  "delta": "-$2.6M",  "trend": rng.uniform(10, 17, 14).tolist(),   "status": "warning"},
    ]


def scenario_pl_bridge():
    return pd.DataFrame({
        "component":  ["Base Revenue", "Demand Surge Impact", "Expediting Cost", "Inventory Build", "Net Margin Delta"],
        "value":      [284.1, 12.3, -3.8, -5.2, 3.3],
        "type":       ["base", "positive", "negative", "negative", "total"],
    })


def budget_vs_forecast():
    months = _months(12)
    budget   = 23 + rng.normal(0, 1.5, 12)
    forecast = budget * rng.uniform(0.96, 1.05, 12)
    actual   = budget[:6] * rng.uniform(0.95, 1.04, 6)
    return pd.DataFrame({
        "month":    months,
        "budget":   budget,
        "forecast": forecast,
        "actual":   list(actual) + [None]*6,
    })


# ─── Risk Monitoring ──────────────────────────────────────────────────────────

def risk_kpis():
    return [
        {"title": "Composite Risk Score", "value": "0.62", "target": "<0.50", "delta": "+0.04", "trend": rng.uniform(0.45, 0.75, 14).tolist(), "status": "danger"},
        {"title": "High-Risk Suppliers",  "value": "3",    "target": "0",     "delta": "+1",    "trend": rng.uniform(0, 5, 14).tolist(),        "status": "danger"},
        {"title": "Disruption Events",    "value": "2",    "target": "0",     "delta": "+2",    "trend": rng.uniform(0, 4, 14).tolist(),        "status": "danger"},
        {"title": "Avg Lead Time CV",     "value": "0.38", "target": "<0.3",  "delta": "+0.05", "trend": rng.uniform(0.2, 0.5, 14).tolist(),   "status": "warning"},
    ]


def risk_probability_impact():
    risks = [
        "Supplier A Delay", "Port Strike APAC", "Raw Mat. Shortage",
        "FX Volatility", "Demand Spike", "IT Outage",
        "Weather Event", "Regulatory Change", "Quality Recall",
    ]
    return pd.DataFrame({
        "risk":        risks,
        "probability": rng.uniform(0.1, 0.9, len(risks)).round(2),
        "impact":      rng.uniform(0.2, 1.0, len(risks)).round(2),
        "category":    rng.choice(["Supply", "Demand", "Operational", "External"], len(risks)),
    })


def mitigation_actions():
    return pd.DataFrame({
        "Risk":       ["Supplier A Delay", "Port Strike APAC", "Raw Mat. Shortage"],
        "Score":      [0.82, 0.74, 0.68],
        "Top Factor": ["On-time rate 61%", "Single-source lane", "Geopolitical score 0.8"],
        "Action":     ["Activate backup Supplier D", "Air-freight buffer 500t", "Dual-source qualification"],
        "Status":     ["In Progress", "Planned", "Planned"],
    })


# ─── Sustainability ───────────────────────────────────────────────────────────

def sustainability_kpis():
    return [
        {"title": "Scope 1 (tCO₂e)",   "value": "4,820",  "target": "4,500", "delta": "+320",   "trend": rng.uniform(4200, 5200, 14).tolist(), "status": "danger"},
        {"title": "Scope 2 (tCO₂e)",   "value": "2,140",  "target": "2,000", "delta": "+140",   "trend": rng.uniform(1900, 2400, 14).tolist(), "status": "warning"},
        {"title": "Scope 3 (tCO₂e)",   "value": "18,320", "target": "17,000","delta": "+1,320", "trend": rng.uniform(16000, 20000, 14).tolist(),"status": "danger"},
        {"title": "Carbon Intensity",   "value": "0.88",   "target": "0.80",  "delta": "+0.08",  "trend": rng.uniform(0.75, 1.0, 14).tolist(),  "status": "danger"},
        {"title": "Renewable Energy %", "value": "34%",    "target": "50%",   "delta": "+4pp",   "trend": rng.uniform(28, 40, 14).tolist(),     "status": "warning"},
        {"title": "SBTi Progress %",    "value": "62%",    "target": "100%",  "delta": "+8pp",   "trend": rng.uniform(50, 68, 14).tolist(),     "status": "warning"},
    ]


def emissions_breakdown():
    return pd.DataFrame({
        "category": ["Road Freight", "Air Freight", "Sea Freight", "Warehousing", "Production", "Last Mile"],
        "tco2e":    [6200, 4100, 3800, 2900, 5800, 2480],
    })


def cost_vs_carbon_pareto():
    scenarios = ["Base", "Modal Shift", "Near-shore", "Green Logistics", "Circular", "SBTi Target"]
    return pd.DataFrame({
        "scenario":  scenarios,
        "cost_usd":  [45.2, 43.8, 47.1, 46.0, 44.5, 48.2],
        "carbon":    [25280, 22100, 23800, 19400, 18200, 16000],
    })


# ─── Regional Planning ────────────────────────────────────────────────────────

def regional_performance():
    regions = ["APAC", "EMEA", "Americas", "SEA", "MEA"]
    return pd.DataFrame({
        "region":        regions,
        "otif":          rng.uniform(88, 97, 5).round(1),
        "plan_achieved": rng.uniform(91, 99, 5).round(1),
        "dos":           rng.uniform(25, 48, 5).round(1),
        "risk_score":    rng.uniform(0.2, 0.8, 5).round(2),
        "iso_a3":        ["SGP", "DEU", "USA", "THA", "SAU"],
    })


def region_vs_plan():
    regions = ["APAC", "EMEA", "Americas", "SEA", "MEA"]
    return pd.DataFrame({
        "region": regions,
        "plan":   rng.uniform(80, 150, 5).round(1),
        "actual": rng.uniform(75, 160, 5).round(1),
    })
